from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sqlite3
import psycopg2
import pymysql
from typing import Dict, List, Tuple, Any, Optional, Union
import logging
from contextlib import contextmanager
from urllib.parse import urlparse

class DatabaseManager:
    """Multi-database support manager with connection pooling and federation"""
    
    def __init__(self):
        self.connections = {}
        self.engines = {}
        self.session_makers = {}
        self.db_types = {}
        self.logger = logging.getLogger(__name__)
    
    def add_connection(self, name: str, connection_string: str, db_type: str = "auto") -> bool:
        """
        Add a database connection
        
        Args:
            name: Connection name/alias
            connection_string: Database connection string
            db_type: Database type (sqlite, postgresql, mysql, or auto-detect)
        
        Returns:
            bool: Success status
        """
        try:
            # Auto-detect database type if not specified
            if db_type == "auto":
                db_type = self._detect_db_type(connection_string)
            
            # Create engine based on database type
            if db_type == "sqlite":
                engine = create_engine(
                    connection_string,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
            elif db_type == "postgresql":
                engine = create_engine(
                    connection_string,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False
                )
            elif db_type == "mysql":
                engine = create_engine(
                    connection_string,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Store connection details
            self.engines[name] = engine
            self.session_makers[name] = sessionmaker(bind=engine)
            self.db_types[name] = db_type
            
            self.logger.info(f"Successfully connected to {name} ({db_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {name}: {e}")
            return False
    
    def _detect_db_type(self, connection_string: str) -> str:
        """Auto-detect database type from connection string"""
        if connection_string.startswith("sqlite"):
            return "sqlite"
        elif connection_string.startswith("postgresql") or connection_string.startswith("postgres"):
            return "postgresql"
        elif connection_string.startswith("mysql"):
            return "mysql"
        elif connection_string.endswith(".db") or connection_string.endswith(".sqlite"):
            return "sqlite"
        else:
            # Default to SQLite for simple file paths
            return "sqlite"
    
    def get_connection(self, name: str):
        """Get database connection by name"""
        if name not in self.engines:
            raise ValueError(f"Connection '{name}' not found")
        return self.engines[name].connect()
    
    @contextmanager
    def get_session(self, name: str):
        """Get database session with automatic cleanup"""
        if name not in self.session_makers:
            raise ValueError(f"Connection '{name}' not found")
        
        session = self.session_makers[name]()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_schema(self, connection_name: str) -> Tuple[Dict[str, List[str]], List[Dict]]:
        """
        Get database schema including tables, columns, and relationships
        
        Returns:
            Tuple of (schema_dict, relationships_list)
        """
        try:
            with self.get_connection(connection_name) as conn:
                inspector = inspect(conn)
                
                # Get all table names
                table_names = inspector.get_table_names()
                
                schema = {}
                for table_name in table_names:
                    columns = inspector.get_columns(table_name)
                    schema[table_name] = [col['name'] for col in columns]
                
                # Get foreign key relationships
                relationships = []
                for table_name in table_names:
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    for fk in foreign_keys:
                        relationships.append({
                            'from_table': table_name,
                            'from_column': fk['constrained_columns'][0],
                            'to_table': fk['referred_table'],
                            'to_column': fk['referred_columns'][0]
                        })
                
                return schema, relationships
                
        except Exception as e:
            self.logger.error(f"Failed to get schema for {connection_name}: {e}")
            return {}, []
    
    def execute_query(self, connection_name: str, query: str) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            with self.get_connection(connection_name) as conn:
                result = conn.execute(text(query))
                
                # Convert to list of dictionaries
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Query execution failed on {connection_name}: {e}")
            raise e
    
    def execute_query_single(self, connection_name: str, query: str) -> Any:
        """Execute query and return single value"""
        try:
            with self.get_connection(connection_name) as conn:
                result = conn.execute(text(query))
                return result.scalar()
                
        except Exception as e:
            self.logger.error(f"Query execution failed on {connection_name}: {e}")
            raise e
    
    def federated_query(self, queries: Dict[str, str]) -> Dict[str, List[Dict]]:
        """
        Execute federated queries across multiple databases
        
        Args:
            queries: Dictionary of connection_name -> query pairs
        
        Returns:
            Dictionary of connection_name -> results
        """
        results = {}
        errors = {}
        
        for connection_name, query in queries.items():
            try:
                results[connection_name] = self.execute_query(connection_name, query)
            except Exception as e:
                errors[connection_name] = str(e)
        
        if errors:
            self.logger.warning(f"Some federated queries failed: {errors}")
        
        return results
    
    def get_table_info(self, connection_name: str, table_name: str) -> Dict:
        """Get detailed information about a specific table"""
        try:
            with self.get_connection(connection_name) as conn:
                inspector = inspect(conn)
                
                # Get columns
                columns = inspector.get_columns(table_name)
                
                # Get primary keys
                primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                # Get row count
                row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys,
                    'row_count': row_count
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {e}")
            return {}
    
    def validate_query(self, connection_name: str, query: str) -> Tuple[bool, str]:
        """
        Validate SQL query without executing it
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with self.get_connection(connection_name) as conn:
                # Use EXPLAIN to validate query syntax
                if self.db_types[connection_name] == "sqlite":
                    validate_query = f"EXPLAIN QUERY PLAN {query}"
                else:
                    validate_query = f"EXPLAIN {query}"
                
                conn.execute(text(validate_query))
                return True, ""
                
        except Exception as e:
            return False, str(e)
    
    def get_connection_info(self, connection_name: str) -> Dict:
        """Get information about a database connection"""
        if connection_name not in self.engines:
            return {}
        
        try:
            with self.get_connection(connection_name) as conn:
                # Get database version info
                if self.db_types[connection_name] == "sqlite":
                    version = conn.execute(text("SELECT sqlite_version()")).scalar()
                elif self.db_types[connection_name] == "postgresql":
                    version = conn.execute(text("SELECT version()")).scalar()
                elif self.db_types[connection_name] == "mysql":
                    version = conn.execute(text("SELECT VERSION()")).scalar()
                else:
                    version = "Unknown"
                
                return {
                    'name': connection_name,
                    'type': self.db_types[connection_name],
                    'version': version,
                    'url': str(self.engines[connection_name].url).replace(self.engines[connection_name].url.password or '', '***')
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get connection info for {connection_name}: {e}")
            return {'name': connection_name, 'type': 'unknown', 'error': str(e)}
    
    def list_connections(self) -> List[str]:
        """List all available connection names"""
        return list(self.engines.keys())
    
    def remove_connection(self, name: str) -> bool:
        """Remove a database connection"""
        try:
            if name in self.engines:
                self.engines[name].dispose()
                del self.engines[name]
                del self.session_makers[name]
                del self.db_types[name]
                self.logger.info(f"Removed connection: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove connection {name}: {e}")
            return False
    
    def close_all(self):
        """Close all database connections"""
        for name, engine in self.engines.items():
            try:
                engine.dispose()
                self.logger.info(f"Closed connection: {name}")
            except Exception as e:
                self.logger.error(f"Error closing connection {name}: {e}")
        
        self.engines.clear()
        self.session_makers.clear()
        self.db_types.clear()

# Global database manager instance
db_manager = DatabaseManager()

# Predefined connection configurations
CONNECTION_CONFIGS = {
    "sqlite_demo": {
        "connection_string": "sqlite:///database.db",
        "db_type": "sqlite"
    },
    "postgresql_example": {
        "connection_string": "postgresql://user:password@localhost:5432/database",
        "db_type": "postgresql"
    },
    "mysql_example": {
        "connection_string": "mysql+pymysql://user:password@localhost:3306/database",
        "db_type": "mysql"
    }
}

def initialize_default_connections():
    """Initialize default database connections"""
    # Add SQLite demo database
    db_manager.add_connection(
        "default",
        "sqlite:///database.db",
        "sqlite"
    )
    
    # Try to add PostgreSQL if available
    try:
        db_manager.add_connection(
            "postgres_demo",
            "postgresql://postgres:password@localhost:5432/neurosql",
            "postgresql"
        )
    except:
        pass
    
    # Try to add MySQL if available
    try:
        db_manager.add_connection(
            "mysql_demo",
            "mysql+pymysql://root:password@localhost:3306/neurosql",
            "mysql"
        )
    except:
        pass
