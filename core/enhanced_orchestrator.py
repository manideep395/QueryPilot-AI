import sqlite3
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Enhanced agents with graceful fallback
try:
    from agents.enhanced_nlu_agent import EnhancedNLUAgent
    from agents.sql_planner_agent import SQLPlannerAgent
    from agents.enhanced_execution_agent import EnhancedExecutionAgent
    from agents.enhanced_reflex_agent import EnhancedReflexAgent
    from agents.enhanced_explanation_agent import EnhancedExplanationAgent
except ImportError as e:
    print(f"⚠️ Warning: Enhanced agents not available ({e}), using basic agents")
    from agents.nlu_agent import NLUAgent
    from agents.execution_agent import ExecutionAgent
    from agents.reflex_agent import ReflexAgent
    from agents.explanation_agent import ExplanationAgent
    # Fallback to basic agents
    EnhancedNLUAgent = NLUAgent
    EnhancedExecutionAgent = ExecutionAgent
    EnhancedReflexAgent = ReflexAgent
    EnhancedExplanationAgent = ExplanationAgent

# Enhanced core components
from core.database_manager import db_manager, initialize_default_connections
from core.performance_optimizer import performance_optimizer
from core.security_manager import security_manager, Permission
from core.sql_safety import validate_sql, SQLSafetyError

class EnhancedOrchestrator:
    """Enhanced NeuroSQL orchestrator with AI, multi-DB, performance, and security"""
    
    def __init__(self, default_database: str = "database.db"):
        # Initialize database manager
        initialize_default_connections()
        
        # Initialize enhanced agents
        self.nlu = EnhancedNLUAgent()
        self.planner = SQLPlannerAgent()
        self.executor = EnhancedExecutionAgent()
        self.reflex = EnhancedReflexAgent()
        self.explanation = EnhancedExplanationAgent()
        
        # Set default database
        self.current_db = "default"
        self.default_database = default_database
        
        print("🚀 Enhanced NeuroSQL Orchestrator Initialized")
        print("✅ AI/ML Integration: Enabled")
        print("✅ Multi-Database Support: Enabled")
        print("✅ Performance Optimization: Enabled")
        print("✅ Security Framework: Enabled")
    
    def handle_query(self, user_input: str, user_id: Optional[str] = None, database: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced query handler with all new features
        
        Args:
            user_input: Natural language query
            user_id: User ID for security and auditing
            database: Database name (uses default if not specified)
        
        Returns:
            Enhanced result with performance metrics and security info
        """
        start_time = time.time()
        
        # Use provided database or default
        target_db = database or self.current_db
        
        try:
            # Security check
            if user_id:
                user = security_manager.get_user(user_id)
                if not user:
                    return {
                        "sql": None,
                        "result": None,
                        "explanation": "User not found or not authenticated",
                        "confidence": 0.0,
                        "error": "authentication_failed",
                        "execution_time": time.time() - start_time
                    }
            
            # Handle special commands
            if user_input.strip().lower() == "show tables":
                return self._handle_show_tables(target_db, user_id)
            elif user_input.strip().lower().startswith("describe "):
                return self._handle_describe_table(user_input, target_db, user_id)
            elif user_input.strip().lower().startswith("import "):
                return self._handle_import_csv(user_input, target_db, user_id)
            elif user_input.strip().lower().startswith("load "):
                return self._handle_load_database(user_input, user_id)
            elif user_input.strip().lower() == "performance report":
                return self._handle_performance_report(user_id)
            elif user_input.strip().lower() == "optimization suggestions":
                return self._handle_optimization_suggestions(user_id)
            
            # Main query processing pipeline
            return self._process_query_pipeline(user_input, target_db, user_id, start_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ System Error: {e}")
            
            return {
                "sql": None,
                "result": None,
                "explanation": f"System error: {e}",
                "confidence": 0.0,
                "error": "system_error",
                "execution_time": execution_time
            }
    
    def _process_query_pipeline(self, user_input: str, database: str, user_id: Optional[str], start_time: float) -> Dict[str, Any]:
        """Main query processing pipeline with all enhancements"""
        
        # Step 1: Get database schema
        print(f"\n[1] Reading database schema from {database}...")
        schema, relations = db_manager.get_schema(database)
        print(f"[Schema]: {len(schema)} tables found")
        
        # Step 2: Enhanced NLU processing
        print("[2] AI-powered question understanding...")
        intent = self.nlu.parse(user_input, schema)
        print(f"[Intent]: {intent}")
        
        # Step 3: SQL planning
        print("[3] Planning SQL query...")
        sql = self.planner.generate_sql(intent, schema, relations, None)
        
        if sql is None:
            raise SQLSafetyError("Planner failed to produce valid SQL")
        
        # Step 4: Security validation
        print("[4] Security validation...")
        if user_id:
            has_permission, security_message = security_manager.check_query_permission(user_id, sql, database)
            if not has_permission:
                return {
                    "sql": sql,
                    "result": None,
                    "explanation": f"Query blocked by security policy: {security_message}",
                    "confidence": 0.0,
                    "error": "security_blocked",
                    "execution_time": time.time() - start_time
                }
        
        # Step 5: SQL safety validation
        print("[5] SQL safety validation...")
        validate_sql(sql, {"tables": schema})
        
        # Step 6: Performance optimization
        print("[6] Performance optimization...")
        optimized_sql, optimizations = performance_optimizer.optimize_query_execution(sql, database)
        if optimizations:
            print(f"[Optimizations]: {optimizations}")
        
        # Step 7: Query execution with performance monitoring
        print("[7] Executing optimized query...")
        execution_start = time.time()
        result = db_manager.execute_query(database, optimized_sql)
        
        # Step 8: Performance analysis
        print("[8] Performance analysis...")
        metrics = performance_optimizer.analyze_query_performance(optimized_sql, database)
        
        # Step 9: Enhanced explanation generation
        print("[9] Generating enhanced explanation...")
        explanation_data = self.explanation.generate_explanation(
            optimized_sql, intent, result, {
                "execution_time": execution_time,
                "performance_score": metrics.get("performance_score", 0) if metrics else 0,
                "optimizations_applied": optimizations,
                "cache_hit": performance_optimizer.cache_enabled and execution_time < 0.1
            }
        )
        
        # Combine all explanations
        detailed_explanation = explanation_data["detailed_explanation"]
        if not detailed_explanation:
            detailed_explanation = explanation_data["primary_explanation"]
        
        # Add insights to explanation
        insights = explanation_data.get("insights", [])
        if insights:
            detailed_explanation += f" | Insights: {'; '.join(insights[:2])}"  # Limit to top 2 insights
        
        # Add suggestions to explanation
        suggestions = explanation_data.get("suggestions", [])
        if suggestions:
            detailed_explanation += f" | Suggestions: {'; '.join(suggestions[:2])}"  # Limit to top 2 suggestions
        
        # Step 10: Security audit logging
        if user_id:
            security_manager._log_audit(
                user_id=user_id,
                action="query_executed",
                resource=database,
                ip_address="system",
                user_agent="orchestrator",
                success=True,
                details={
                    "query": user_input,
                    "sql": optimized_sql,
                    "execution_time": execution_time,
                    "rows_returned": len(result) if result else 0
                }
            )
        
        total_execution_time = time.time() - start_time
        
        return {
            "sql": optimized_sql,
            "result": result,
            "explanation": detailed_explanation,
            "confidence": intent.get("confidence", 0.8),
            "execution_time": total_execution_time,
            "performance_metrics": {
                "query_execution_time": execution_time,
                "rows_returned": len(result) if result else 0,
                "optimizations_applied": optimizations,
                "performance_score": metrics.get("performance_score", 0) if metrics else 0
            },
            "ai_enhancements": {
                "nlu_method": intent.get("method", "regex"),
                "temporal_intent": intent.get("temporal", {}),
                "comparative_intent": intent.get("comparative", {}),
                "semantic_score": intent.get("semantic_score", 0.0)
            },
            "security_info": {
                "user_authenticated": user_id is not None,
                "permissions_checked": user_id is not None
            }
        }
    
    def _generate_enhanced_explanation(self, intent: Dict, sql: str, metrics, optimizations: List[str]) -> str:
        """Generate enhanced explanation with AI insights"""
        explanation_parts = []
        
        # Basic explanation
        if intent.get("aggregation"):
            explanation_parts.append(f"I calculated the {intent['aggregation'].lower()}")
        else:
            explanation_parts.append("I retrieved the data")
        
        if intent.get("table"):
            explanation_parts.append(f"from the {intent['table']} table")
        
        if intent.get("where_column"):
            explanation_parts.append(f"filtering where {intent['where_column']} {intent['where_operator']} {intent['where_value']}")
        
        # AI enhancements
        if intent.get("temporal"):
            temporal = intent["temporal"]
            if "time_range" in temporal:
                explanation_parts.append(f"for the {temporal['time_range'].replace('_', ' ')}")
        
        if intent.get("comparative"):
            comparative = intent["comparative"]
            if "comparison" in comparative:
                explanation_parts.append(f"using {comparative['comparison'].replace('_', ' ')} comparison")
        
        # Performance insights
        if metrics.execution_time > 1.0:
            explanation_parts.append(f"(Query took {metrics.execution_time:.2f}s - consider optimization)")
        
        if optimizations:
            explanation_parts.append(f"(Applied {len(optimizations)} automatic optimizations)")
        
        # Confidence info
        confidence = intent.get("confidence", 0.8)
        if confidence < 0.7:
            explanation_parts.append(f"(Confidence: {confidence:.1%} - please verify results)")
        
        return " ".join(explanation_parts) + "."
    
    def _calculate_performance_score(self, metrics) -> float:
        """Calculate performance score (0-100)"""
        score = 100.0
        
        # Deduct points for slow execution
        if metrics.execution_time > 2.0:
            score -= (metrics.execution_time - 2.0) * 20
        elif metrics.execution_time > 1.0:
            score -= (metrics.execution_time - 1.0) * 10
        
        # Deduct points for high resource usage
        if metrics.cpu_usage > 50:
            score -= (metrics.cpu_usage - 50) * 0.5
        
        if metrics.memory_usage > 30:
            score -= (metrics.memory_usage - 30) * 0.3
        
        # Bonus points for optimizations
        if metrics.optimization_suggestions:
            score += len(metrics.optimization_suggestions) * 2
        
        return max(0.0, min(100.0, score))
    
    def _handle_show_tables(self, database: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle show tables command"""
        try:
            tables = list(db_manager.get_schema(database)[0].keys())
            return {
                "sql": None,
                "result": tables,
                "explanation": f"Listed all tables in {database} database.",
                "confidence": 1.0,
                "database": database
            }
        except Exception as e:
            return {
                "sql": None,
                "result": None,
                "explanation": f"Failed to list tables: {e}",
                "confidence": 0.0,
                "error": "database_error"
            }
    
    def _handle_describe_table(self, user_input: str, database: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle describe table command"""
        try:
            table_name = user_input.strip().split()[1]
            table_info = db_manager.get_table_info(database, table_name)
            
            return {
                "sql": None,
                "result": table_info,
                "explanation": f"Described table {table_name} in {database} database.",
                "confidence": 1.0,
                "database": database
            }
        except Exception as e:
            return {
                "sql": None,
                "result": None,
                "explanation": f"Failed to describe table: {e}",
                "confidence": 0.0,
                "error": "database_error"
            }
    
    def _handle_import_csv(self, user_input: str, database: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle CSV import command"""
        # This would need to be implemented based on your CSV import requirements
        return {
            "sql": None,
            "result": None,
            "explanation": "CSV import functionality needs to be implemented for multi-database support.",
            "confidence": 0.0,
            "error": "not_implemented"
        }
    
    def _handle_load_database(self, user_input: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle database switching"""
        try:
            new_db = user_input.strip()[5:].strip()
            if new_db in db_manager.list_connections():
                self.current_db = new_db
                return {
                    "sql": None,
                    "result": None,
                    "explanation": f"Switched to database: {new_db}",
                    "confidence": 1.0,
                    "database": new_db
                }
            else:
                return {
                    "sql": None,
                    "result": None,
                    "explanation": f"Database '{new_db}' not found. Available: {db_manager.list_connections()}",
                    "confidence": 0.0,
                    "error": "database_not_found"
                }
        except Exception as e:
            return {
                "sql": None,
                "result": None,
                "explanation": f"Failed to switch database: {e}",
                "confidence": 0.0,
                "error": "database_error"
            }
    
    def _handle_performance_report(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle performance report command"""
        if user_id:
            user = security_manager.get_user(user_id)
            if not user or not security_manager.check_permission(user_id, Permission.READ_DATA):
                return {
                    "sql": None,
                    "result": None,
                    "explanation": "No permission to view performance reports",
                    "confidence": 0.0,
                    "error": "permission_denied"
                }
        
        report = performance_optimizer.get_performance_report()
        return {
            "sql": None,
            "result": report,
            "explanation": "Generated performance report for the last 24 hours.",
            "confidence": 1.0
        }
    
    def _handle_optimization_suggestions(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Handle optimization suggestions command"""
        if user_id:
            user = security_manager.get_user(user_id)
            if not user or not security_manager.check_permission(user_id, Permission.READ_DATA):
                return {
                    "sql": None,
                    "result": None,
                    "explanation": "No permission to view optimization suggestions",
                    "confidence": 0.0,
                    "error": "permission_denied"
                }
        
        suggestions = performance_optimizer.get_optimization_recommendations()
        return {
            "sql": None,
            "result": suggestions,
            "explanation": "Generated optimization suggestions based on query history.",
            "confidence": 1.0
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "orchestrator": "enhanced",
            "ai_integration": "enabled",
            "multi_database": {
                "supported": True,
                "connections": db_manager.list_connections(),
                "default": self.current_db
            },
            "performance_optimization": {
                "enabled": True,
                "cache_enabled": performance_optimizer.cache_enabled,
                "metrics_collected": len(performance_optimizer.query_history)
            },
            "security": {
                "enabled": True,
                "users_registered": len(security_manager.users),
                "audit_logs": len(security_manager.audit_logs)
            },
            "supported_databases": ["SQLite", "PostgreSQL", "MySQL"],
            "features": [
                "AI-powered NLU with transformers",
                "Multi-database support",
                "Query performance optimization",
                "Security and authentication",
                "Real-time monitoring",
                "Automatic caching"
            ]
        }

# Enhanced version for backward compatibility
class Orchestrator(EnhancedOrchestrator):
    """Backward compatible orchestrator"""
    def __init__(self, db_path: str):
        # Map old db_path to new database manager
        if db_path != "database.db":
            # Add custom database connection
            db_manager.add_connection("custom", f"sqlite:///{db_path}", "sqlite")
        super().__init__(db_path)
