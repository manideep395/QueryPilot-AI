import re
import time
import psutil
import redis
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
from sqlalchemy import text
from core.database_manager import db_manager

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query: str
    execution_time: float
    rows_returned: int
    cpu_usage: float
    memory_usage: float
    timestamp: datetime
    database: str
    optimization_suggestions: List[str]

@dataclass
class OptimizationSuggestion:
    """Query optimization suggestion"""
    type: str  # 'index', 'query_rewrite', 'partitioning', 'caching'
    description: str
    impact: str  # 'high', 'medium', 'low'
    sql_suggestion: Optional[str] = None
    index_suggestion: Optional[str] = None

class PerformanceOptimizer:
    """Advanced query performance optimization and monitoring system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.cache_enabled = True
            logging.info("Redis cache connected successfully")
        except:
            self.cache_enabled = False
            logging.warning("Redis not available, caching disabled")
        
        self.query_history = []
        self.optimization_cache = {}
        self.logger = logging.getLogger(__name__)
    
    def analyze_query_performance(self, query: str, database: str = "default") -> QueryMetrics:
        """Analyze query performance and collect metrics"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        try:
            # Execute query and measure performance
            result = db_manager.execute_query(database, query)
            execution_time = time.time() - start_time
            
            # Calculate resource usage
            end_cpu = psutil.cpu_percent()
            end_memory = psutil.virtual_memory().percent
            
            metrics = QueryMetrics(
                query=query,
                execution_time=execution_time,
                rows_returned=len(result) if result else 0,
                cpu_usage=end_cpu - start_cpu,
                memory_usage=end_memory - start_memory,
                timestamp=datetime.now(),
                database=database,
                optimization_suggestions=[]
            )
            
            # Generate optimization suggestions
            metrics.optimization_suggestions = self._generate_optimization_suggestions(query, metrics, database)
            
            # Store metrics
            self._store_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Query analysis failed: {e}")
            raise e
    
    def _generate_optimization_suggestions(self, query: str, metrics: QueryMetrics, database: str) -> List[OptimizationSuggestion]:
        """Generate intelligent optimization suggestions"""
        suggestions = []
        
        # Performance-based suggestions
        if metrics.execution_time > 1.0:  # Slow query
            suggestions.append(OptimizationSuggestion(
                type="query_rewrite",
                description="Query execution time is high. Consider optimization.",
                impact="high",
                sql_suggestion=self._suggest_query_rewrite(query)
            ))
        
        # Row count based suggestions
        if metrics.rows_returned > 10000:
            suggestions.append(OptimizationSuggestion(
                type="pagination",
                description="Large result set returned. Consider pagination.",
                impact="medium"
            ))
        
        # Index suggestions
        index_suggestions = self._suggest_indexes(query, database)
        suggestions.extend(index_suggestions)
        
        # Caching suggestions
        if self._should_cache(query, metrics):
            suggestions.append(OptimizationSuggestion(
                type="caching",
                description="Frequent query detected. Consider caching results.",
                impact="high"
            ))
        
        return suggestions
    
    def _suggest_query_rewrite(self, query: str) -> str:
        """Suggest query rewrite optimizations"""
        suggestions = []
        
        # Avoid SELECT *
        if re.search(r'SELECT\s+\*', query, re.IGNORECASE):
            suggestions.append("Replace SELECT * with specific columns")
        
        # Add LIMIT for large tables
        if not re.search(r'LIMIT\s+\d+', query, re.IGNORECASE):
            suggestions.append("Consider adding LIMIT clause")
        
        # Suggest EXISTS instead of IN for subqueries
        if re.search(r'\bIN\s*\(', query, re.IGNORECASE):
            suggestions.append("Consider using EXISTS instead of IN for better performance")
        
        # Suggest JOIN optimization
        if query.upper().count('JOIN') > 2:
            suggestions.append("Multiple JOINs detected. Consider breaking into smaller queries")
        
        return "; ".join(suggestions) if suggestions else "Query structure looks good"
    
    def _suggest_indexes(self, query: str, database: str) -> List[OptimizationSuggestion]:
        """Suggest database indexes based on query patterns"""
        suggestions = []
        
        try:
            # Extract WHERE conditions
            where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)', query, re.IGNORECASE)
            if where_match:
                where_clause = where_match.group(1)
                
                # Extract column names from WHERE clause
                columns = re.findall(r'(\w+)\s*(?:=|>|<|LIKE|IN)', where_clause, re.IGNORECASE)
                
                for column in columns:
                    suggestions.append(OptimizationSuggestion(
                        type="index",
                        description=f"Consider adding index on column: {column}",
                        impact="medium",
                        index_suggestion=f"CREATE INDEX idx_{column} ON table_name ({column})"
                    ))
            
            # Extract JOIN conditions
            join_matches = re.findall(r'JOIN\s+\w+\s+ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)', query, re.IGNORECASE)
            for join_condition in join_matches:
                for column_ref in join_condition:
                    column = column_ref.split('.')[-1]
                    suggestions.append(OptimizationSuggestion(
                        type="index",
                        description=f"Consider adding index for JOIN column: {column}",
                        impact="high",
                        index_suggestion=f"CREATE INDEX idx_join_{column} ON table_name ({column})"
                    ))
            
        except Exception as e:
            self.logger.error(f"Index suggestion failed: {e}")
        
        return suggestions
    
    def _should_cache(self, query: str, metrics: QueryMetrics) -> bool:
        """Determine if query should be cached"""
        # Don't cache queries with time-sensitive functions
        time_sensitive = re.search(r'NOW\(\)|CURRENT_TIMESTAMP|GETDATE\(\)', query, re.IGNORECASE)
        if time_sensitive:
            return False
        
        # Cache frequently executed queries
        query_hash = hash(query.lower().strip())
        cache_count = self._get_cache_count(query_hash)
        
        return cache_count > 3 or metrics.execution_time > 0.5
    
    def _get_cache_count(self, query_hash: int) -> int:
        """Get cache hit count for query"""
        if not self.cache_enabled:
            return 0
        
        try:
            count = self.redis_client.get(f"query_count:{query_hash}")
            return int(count) if count else 0
        except:
            return 0
    
    def _store_metrics(self, metrics: QueryMetrics):
        """Store query metrics for analysis"""
        self.query_history.append(metrics)
        
        # Keep only last 1000 metrics in memory
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-1000:]
        
        # Store in Redis if available
        if self.cache_enabled:
            try:
                metrics_dict = {
                    'query': metrics.query,
                    'execution_time': metrics.execution_time,
                    'rows_returned': metrics.rows_returned,
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'timestamp': metrics.timestamp.isoformat(),
                    'database': metrics.database
                }
                
                self.redis_client.lpush("query_metrics", json.dumps(metrics_dict))
                self.redis_client.ltrim("query_metrics", 0, 999)  # Keep last 1000
                
                # Update query count
                query_hash = hash(metrics.query.lower().strip())
                self.redis_client.incr(f"query_count:{query_hash}")
                
            except Exception as e:
                self.logger.error(f"Failed to store metrics in Redis: {e}")
    
    def get_performance_report(self, hours: int = 24) -> Dict:
        """Generate performance report for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics by time
        recent_metrics = [m for m in self.query_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"message": "No metrics available for the specified period"}
        
        # Calculate statistics
        total_queries = len(recent_metrics)
        avg_execution_time = sum(m.execution_time for m in recent_metrics) / total_queries
        avg_rows_returned = sum(m.rows_returned for m in recent_metrics) / total_queries
        
        # Find slowest queries
        slowest_queries = sorted(recent_metrics, key=lambda x: x.execution_time, reverse=True)[:5]
        
        # Find most resource-intensive queries
        resource_intensive = sorted(recent_metrics, key=lambda x: x.cpu_usage + x.memory_usage, reverse=True)[:5]
        
        return {
            "period_hours": hours,
            "total_queries": total_queries,
            "avg_execution_time": round(avg_execution_time, 3),
            "avg_rows_returned": round(avg_rows_returned, 1),
            "slowest_queries": [
                {
                    "query": q.query[:100] + "..." if len(q.query) > 100 else q.query,
                    "execution_time": round(q.execution_time, 3),
                    "rows_returned": q.rows_returned,
                    "timestamp": q.timestamp.isoformat()
                }
                for q in slowest_queries
            ],
            "resource_intensive": [
                {
                    "query": q.query[:100] + "..." if len(q.query) > 100 else q.query,
                    "cpu_usage": round(q.cpu_usage, 2),
                    "memory_usage": round(q.memory_usage, 2),
                    "timestamp": q.timestamp.isoformat()
                }
                for q in resource_intensive
            ]
        }
    
    def get_optimization_recommendations(self, database: str = "default") -> List[Dict]:
        """Get comprehensive optimization recommendations"""
        recommendations = []
        
        # Analyze recent queries
        recent_metrics = self.query_history[-100:] if self.query_history else []
        
        # Index recommendations
        index_suggestions = {}
        for metrics in recent_metrics:
            for suggestion in metrics.optimization_suggestions:
                if suggestion.type == "index" and suggestion.index_suggestion:
                    if suggestion.index_suggestion not in index_suggestions:
                        index_suggestions[suggestion.index_suggestion] = {
                            "description": suggestion.description,
                            "impact": suggestion.impact,
                            "frequency": 0
                        }
                    index_suggestions[suggestion.index_suggestion]["frequency"] += 1
        
        # Sort by frequency and impact
        sorted_suggestions = sorted(
            index_suggestions.items(),
            key=lambda x: (x[1]["frequency"], x[1]["impact"]),
            reverse=True
        )
        
        for suggestion, details in sorted_suggestions[:10]:  # Top 10 suggestions
            recommendations.append({
                "type": "index",
                "sql": suggestion,
                "description": details["description"],
                "impact": details["impact"],
                "frequency": details["frequency"]
            })
        
        # Query rewrite recommendations
        rewrite_suggestions = {}
        for metrics in recent_metrics:
            if metrics.execution_time > 1.0:  # Slow queries
                for suggestion in metrics.optimization_suggestions:
                    if suggestion.type == "query_rewrite":
                        query_hash = hash(metrics.query)
                        if query_hash not in rewrite_suggestions:
                            rewrite_suggestions[query_hash] = {
                                "query": metrics.query,
                                "suggestion": suggestion.description,
                                "avg_execution_time": metrics.execution_time,
                                "frequency": 1
                            }
                        else:
                            rewrite_suggestions[query_hash]["frequency"] += 1
        
        for details in rewrite_suggestions.values():
            if details["frequency"] > 2:  # Frequently slow queries
                recommendations.append({
                    "type": "query_rewrite",
                    "query": details["query"][:100] + "..." if len(details["query"]) > 100 else details["query"],
                    "suggestion": details["suggestion"],
                    "avg_execution_time": round(details["avg_execution_time"], 3),
                    "frequency": details["frequency"]
                })
        
        return recommendations
    
    def optimize_query_execution(self, query: str, database: str = "default") -> Tuple[str, List[str]]:
        """Automatically optimize query before execution"""
        optimizations = []
        optimized_query = query
        
        # Add LIMIT if not present and query is potentially expensive
        if not re.search(r'LIMIT\s+\d+', optimized_query, re.IGNORECASE):
            # Check if it's a SELECT query without LIMIT
            if re.match(r'^\s*SELECT\s+', optimized_query, re.IGNORECASE):
                optimized_query += " LIMIT 1000"
                optimizations.append("Added LIMIT 1000 to prevent excessive results")
        
        # Optimize JOIN order (simplified)
        if 'JOIN' in optimized_query.upper():
            # This is a simplified optimization - real JOIN order optimization
            # would require query parsing and cost estimation
            optimizations.append("JOIN order optimization suggested")
        
        return optimized_query, optimizations
    
    def clear_cache(self):
        """Clear performance cache"""
        self.query_history.clear()
        self.optimization_cache.clear()
        
        if self.cache_enabled:
            try:
                self.redis_client.delete("query_metrics")
                # Clear query count keys
                for key in self.redis_client.scan_iter(match="query_count:*"):
                    self.redis_client.delete(key)
                self.logger.info("Performance cache cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear Redis cache: {e}")

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
