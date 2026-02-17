"""
Enhanced Execution Agent for NeuroSQL v2.0
Supports multi-database execution, performance monitoring, and enhanced error handling
"""

import sqlite3
import csv
import time
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from rich.table import Table
from rich.console import Console
from datetime import datetime

# Import enhanced database manager
from core.database_manager import db_manager

console = Console()

class EnhancedExecutionAgent:
    """Enhanced execution agent with multi-database support and performance monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.execution_history = []
        self.performance_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
    
    def execute(self, sql: str, database: str = "default") -> Tuple[bool, Union[List[Dict], str]]:
        """
        Execute SQL query with enhanced error handling and performance monitoring
        
        Args:
            sql: SQL query to execute
            database: Database name to use
            
        Returns:
            Tuple of (success, result_or_error_message)
        """
        start_time = time.time()
        
        try:
            self.performance_metrics["total_queries"] += 1
            
            # Use enhanced database manager
            if database in db_manager.list_connections():
                result = db_manager.execute_query(database, sql)
                execution_time = time.time() - start_time
                
                # Update performance metrics
                self.performance_metrics["successful_queries"] += 1
                self.performance_metrics["total_execution_time"] += execution_time
                self.performance_metrics["average_execution_time"] = (
                    self.performance_metrics["total_execution_time"] / 
                    self.performance_metrics["successful_queries"]
                )
                
                # Log execution
                self._log_execution(sql, database, True, execution_time, len(result) if result else 0)
                
                # Display results with rich formatting
                self._display_results(result, sql, execution_time)
                
                return True, result
                
            else:
                error_msg = f"Database '{database}' not found. Available: {db_manager.list_connections()}"
                self.performance_metrics["failed_queries"] += 1
                self._log_execution(sql, database, False, time.time() - start_time, 0, error_msg)
                return False, error_msg
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Query execution failed: {str(e)}"
            self.performance_metrics["failed_queries"] += 1
            self._log_execution(sql, database, False, execution_time, 0, str(e))
            self.logger.error(f"SQL execution error: {e}")
            return False, error_msg
    
    def _display_results(self, result: List[Dict], sql: str, execution_time: float):
        """Display query results with enhanced formatting"""
        if not result:
            console.print(f"📊 Query executed successfully (no results returned)", style="green")
            console.print(f"⏱️  Execution time: {execution_time:.3f}s", style="blue")
            console.print(f"🔍 SQL: {sql}", style="dim")
            return
        
        # Create rich table
        table = Table(title=f"Query Results ({len(result)} rows)")
        
        # Add columns
        if result:
            columns = list(result[0].keys())
            for col in columns:
                table.add_column(col, style="cyan")
        
        # Add rows
        for row in result:
            # Convert all values to strings for display
            display_row = []
            for value in row.values():
                if value is None:
                    display_row.append("NULL")
                elif isinstance(value, (int, float)):
                    display_row.append(str(value))
                else:
                    display_row.append(str(value)[:50] + "..." if len(str(value)) > 50 else str(value))
            
            table.add_row(*display_row)
        
        # Display table and metadata
        console.print(table)
        console.print(f"⏱️  Execution time: {execution_time:.3f}s", style="blue")
        console.print(f"📊 Rows returned: {len(result)}", style="green")
        
        # Show performance info if available
        if execution_time > 1.0:
            console.print(f"⚠️  Slow query detected ({execution_time:.2f}s). Consider optimization.", style="yellow")
    
    def _log_execution(self, sql: str, database: str, success: bool, execution_time: float, 
                     rows_returned: int, error_msg: str = None):
        """Log query execution for monitoring and analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sql": sql[:200] + "..." if len(sql) > 200 else sql,
            "database": database,
            "success": success,
            "execution_time": execution_time,
            "rows_returned": rows_returned,
            "error_message": error_msg
        }
        
        self.execution_history.append(log_entry)
        
        # Keep only last 1000 executions in memory
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
        
        # Log to file for persistent storage
        self.logger.info(f"Query executed - Success: {success}, Time: {execution_time:.3f}s, Rows: {rows_returned}")
    
    def import_csv(self, database: str, csv_path: str, table_name: str) -> bool:
        """
        Enhanced CSV import with validation and error handling
        
        Args:
            database: Target database name
            csv_path: Path to CSV file
            table_name: Name of table to create
            
        Returns:
            bool: Success status
        """
        try:
            # Validate CSV file exists
            import os
            if not os.path.exists(csv_path):
                console.print(f"❌ CSV file not found: {csv_path}", style="red")
                return False
            
            # Read and validate CSV
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                
                if not headers:
                    console.print("❌ CSV file is empty", style="red")
                    return False
                
                # Validate headers
                if any(not header or header.strip() == "" for header in headers):
                    console.print("❌ CSV contains empty column names", style="red")
                    return False
                
                # Create table with enhanced schema
                columns = ", ".join([f'"{h.strip()}" TEXT' for h in headers])
                
                # Use database manager for multi-DB support
                if database in db_manager.list_connections():
                    # For SQLite, we need to use the raw connection
                    conn = db_manager.engines[database].connect()
                    cursor = conn.cursor()
                    
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
                    
                    # Insert rows with batch processing for better performance
                    rows_inserted = 0
                    batch_size = 1000
                    batch_data = []
                    
                    for row in reader:
                        if row and len(row) == len(headers):
                            batch_data.append(row)
                            rows_inserted += 1
                            
                            if len(batch_data) >= batch_size:
                                placeholders = ", ".join(["?"] * len(row))
                                cursor.executemany(
                                    f"INSERT INTO {table_name} VALUES ({placeholders})", 
                                    batch_data
                                )
                                batch_data = []
                    
                    # Insert remaining batch
                    if batch_data:
                        placeholders = ", ".join(["?"] * len(headers))
                        cursor.executemany(
                            f"INSERT INTO {table_name} VALUES ({placeholders})", 
                            batch_data
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    console.print(f"✅ Successfully imported {rows_inserted} rows from {csv_path}", style="green")
                    console.print(f"📊 Created table: {table_name} with columns: {', '.join(headers)}", style="blue")
                    
                    # Log import operation
                    self.logger.info(f"CSV imported: {csv_path} -> {table_name} ({rows_inserted} rows)")
                    
                    return True
                else:
                    console.print(f"❌ Database '{database}' not available", style="red")
                    return False
                    
        except Exception as e:
            console.print(f"❌ CSV import failed: {str(e)}", style="red")
            self.logger.error(f"CSV import error: {e}")
            return False
    
    def show_tables(self, database: str = "default") -> List[str]:
        """
        Enhanced table listing with multi-database support
        
        Args:
            database: Database name to list tables from
            
        Returns:
            List[str]: List of table names
        """
        try:
            if database in db_manager.list_connections():
                schema, _ = db_manager.get_schema(database)
                tables = list(schema.keys())
                
                # Display with rich formatting
                table = Table(title=f"Tables in '{database}' Database")
                table.add_column("Table Name", style="cyan")
                table.add_column("Columns", style="green")
                
                for table_name in tables:
                    column_count = len(schema.get(table_name, []))
                    table.add_row(table_name, str(column_count))
                
                console.print(table)
                return tables
            else:
                console.print(f"❌ Database '{database}' not found", style="red")
                console.print(f"Available databases: {db_manager.list_connections()}", style="yellow")
                return []
                
        except Exception as e:
            console.print(f"❌ Failed to list tables: {str(e)}", style="red")
            self.logger.error(f"Table listing error: {e}")
            return []
    
    def describe_table(self, database: str, table_name: str) -> Optional[List[Dict]]:
        """
        Enhanced table description with detailed information
        
        Args:
            database: Database name
            table_name: Table name to describe
            
        Returns:
            List[Dict]: Table schema information or None if not found
        """
        try:
            if database in db_manager.list_connections():
                table_info = db_manager.get_table_info(database, table_name)
                
                if not table_info:
                    console.print(f"❌ Table '{table_name}' not found in database '{database}'", style="red")
                    return None
                
                # Display with rich formatting
                console.print(f"📋 Table: {table_name}", style="bold blue")
                console.print(f"🗄️  Database: {database}", style="green")
                console.print(f"📊 Row Count: {table_info.get('row_count', 'Unknown')}", style="yellow")
                
                # Display columns
                if table_info.get("columns"):
                    table = Table(title="Table Schema")
                    table.add_column("Column Name", style="cyan")
                    table.add_column("Type", style="green")
                    table.add_column("Primary Key", style="yellow")
                    
                    for col in table_info["columns"]:
                        is_primary = col["name"] in table_info.get("primary_keys", [])
                        pk_indicator = "✅" if is_primary else "❌"
                        table.add_row(col["name"], col["type"], pk_indicator)
                    
                    console.print(table)
                
                # Display foreign keys
                if table_info.get("foreign_keys"):
                    console.print("\n🔗 Foreign Key Relationships:", style="bold blue")
                    for fk in table_info["foreign_keys"]:
                        console.print(f"  • {fk['from_column']} -> {fk['referred_table']}.{fk['referred_column']}", 
                                     style="green")
                
                return table_info.get("columns")
            else:
                console.print(f"❌ Database '{database}' not found", style="red")
                return None
                
        except Exception as e:
            console.print(f"❌ Failed to describe table: {str(e)}", style="red")
            self.logger.error(f"Table description error: {e}")
            return None
    
    def read_schema(self, database: str = "default") -> Tuple[Dict[str, List[str]], List[Dict]]:
        """
        Enhanced schema reading with multi-database support
        
        Args:
            database: Database name to read schema from
            
        Returns:
            Tuple of (schema_dict, relationships_list)
        """
        try:
            return db_manager.get_schema(database)
        except Exception as e:
            self.logger.error(f"Schema reading error: {e}")
            return {}, []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        # Calculate additional metrics
        success_rate = 0
        if self.performance_metrics["total_queries"] > 0:
            success_rate = (self.performance_metrics["successful_queries"] / 
                          self.performance_metrics["total_queries"]) * 100
        
        return {
            **self.performance_metrics,
            "success_rate": success_rate,
            "recent_executions": self.execution_history[-10:],  # Last 10 executions
            "execution_history_size": len(self.execution_history)
        }
    
    def clear_execution_history(self):
        """Clear execution history and reset metrics"""
        self.execution_history.clear()
        self.performance_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
        console.print("🗑️ Execution history and metrics cleared", style="green")
    
    def export_execution_history(self, filename: str = None) -> bool:
        """Export execution history to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"execution_history_{timestamp}.csv"
        
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if self.execution_history:
                    fieldnames = self.execution_history[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader(fieldnames)
                    writer.writerows(self.execution_history)
            
            console.print(f"📁 Execution history exported to {filename}", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to export history: {str(e)}", style="red")
            self.logger.error(f"History export error: {e}")
            return False

# Backward compatibility alias
ExecutionAgent = EnhancedExecutionAgent
