"""
Enhanced Explanation Agent for NeuroSQL v2.0
Advanced natural language explanations with AI insights and context awareness
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

class EnhancedExplanationAgent:
    """Enhanced explanation agent with AI-powered insights and contextual understanding"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.explanation_history = []
        self.explanation_patterns = self._load_explanation_patterns()
        
    def _load_explanation_patterns(self) -> Dict[str, Dict]:
        """Load explanation templates and patterns"""
        return {
            "aggregation": {
                "COUNT": {
                    "template": "I counted the {target} from {source}",
                    "detailed": "Found {count} {target} in the {source}",
                    "natural": "There are {count} {target} in {source}"
                },
                "AVG": {
                    "template": "I calculated the average {target} from {source}",
                    "detailed": "The average {target} across {source} is {value}",
                    "natural": "On average, the {target} in {source} is {value}"
                },
                "MAX": {
                    "template": "I found the maximum {target} from {source}",
                    "detailed": "The highest {target} in {source} is {value}",
                    "natural": "The {target} with the highest value in {source} is {value}"
                },
                "MIN": {
                    "template": "I found the minimum {target} from {source}",
                    "detailed": "The lowest {target} in {source} is {value}",
                    "natural": "The {target} with the lowest value in {source} is {value}"
                },
                "SUM": {
                    "template": "I calculated the sum of {target} from {source}",
                    "detailed": "The total {target} across {source} is {value}",
                    "natural": "The combined {target} in {source} is {value}"
                }
            },
            "filtering": {
                "comparison": {
                    "greater_than": "I filtered {source} where {column} is greater than {value}",
                    "less_than": "I filtered {source} where {column} is less than {value}",
                    "equal": "I filtered {source} where {column} equals {value}",
                    "between": "I filtered {source} where {column} is between {value1} and {value2}"
                },
                "temporal": {
                    "last_month": "I found {source} from last month",
                    "this_year": "I found {source} from this year",
                    "last_week": "I found {source} from last week"
                }
            },
            "joins": {
                "simple": "I combined {table1} and {table2} to show related information",
                "complex": "I analyzed the relationship between {table1} and {table2} based on {condition}"
            }
        }
    
    def generate_explanation(self, sql: str, intent: Dict[str, Any], result: List[Dict] = None, 
                          execution_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive explanation with AI insights
        
        Args:
            sql: Generated SQL query
            intent: Parsed user intent
            result: Query execution results
            execution_context: Performance and execution context
            
        Returns:
            Dict containing explanation and metadata
        """
        try:
            explanation_data = {
                "primary_explanation": "",
                "detailed_explanation": "",
                "natural_explanation": "",
                "technical_details": {},
                "insights": [],
                "confidence_factors": {},
                "execution_summary": {},
                "suggestions": []
            }
            
            # Generate primary explanation
            explanation_data["primary_explanation"] = self._generate_primary_explanation(sql, intent)
            
            # Generate detailed explanation with results
            if result:
                explanation_data["detailed_explanation"] = self._generate_detailed_explanation(sql, intent, result)
                explanation_data["natural_explanation"] = self._generate_natural_explanation(sql, intent, result)
            
            # Add technical details
            explanation_data["technical_details"] = self._analyze_technical_details(sql, intent)
            
            # Generate insights
            explanation_data["insights"] = self._generate_insights(sql, intent, result, execution_context)
            
            # Add confidence factors
            explanation_data["confidence_factors"] = self._analyze_confidence_factors(intent, execution_context)
            
            # Add execution summary
            explanation_data["execution_summary"] = self._generate_execution_summary(execution_context, result)
            
            # Generate suggestions
            explanation_data["suggestions"] = self._generate_suggestions(sql, intent, result, execution_context)
            
            # Log explanation for analytics
            self._log_explanation(explanation_data)
            
            return explanation_data
            
        except Exception as e:
            self.logger.error(f"Explanation generation error: {e}")
            return {
                "primary_explanation": f"I generated a SQL query to answer your question, but encountered an error: {str(e)}",
                "detailed_explanation": "Error occurred during explanation generation",
                "natural_explanation": "Please try rephrasing your question",
                "technical_details": {"error": str(e)},
                "insights": [],
                "confidence_factors": {},
                "execution_summary": {},
                "suggestions": ["Try rephrasing your question with different keywords"]
            }
    
    def _generate_primary_explanation(self, sql: str, intent: Dict[str, Any]) -> str:
        """Generate primary explanation based on intent"""
        parts = []
        
        # Start with action
        if intent.get("aggregation"):
            agg_type = intent["aggregation"]
            target = self._get_target_description(intent)
            source = self._get_source_description(intent)
            
            if agg_type in self.explanation_patterns["aggregation"]:
                template = self.explanation_patterns["aggregation"][agg_type]["template"]
                parts.append(template.format(target=target, source=source))
        
        elif intent.get("where_column"):
            # Filtering query
            target = self._get_target_description(intent)
            source = self._get_source_description(intent)
            
            if intent.get("where_operator"):
                operator = intent["where_operator"]
                value = intent["where_value"]
                
                if operator == ">":
                    parts.append(f"I filtered {source} where {target} is greater than {value}")
                elif operator == "<":
                    parts.append(f"I filtered {source} where {target} is less than {value}")
                elif operator == "=":
                    parts.append(f"I filtered {source} where {target} equals {value}")
                else:
                    parts.append(f"I filtered {source} based on {target}")
            else:
                parts.append(f"I retrieved {target} from {source}")
        
        else:
            # Simple retrieval
            target = self._get_target_description(intent)
            source = self._get_source_description(intent)
            parts.append(f"I retrieved {target} from {source}")
        
        # Add temporal context if present
        if intent.get("temporal"):
            temporal_info = intent["temporal"]
            if "time_range" in temporal_info:
                time_desc = temporal_info["time_range"].replace("_", " ")
                parts.append(f"for the {time_desc}")
        
        # Add comparative context if present
        if intent.get("comparative"):
            comp_info = intent["comparative"]
            if "comparison" in comp_info:
                comp_desc = comp_info["comparison"].replace("_", " ")
                parts.append(f"using {comp_desc} comparison")
        
        return " ".join(parts) + "."
    
    def _generate_detailed_explanation(self, sql: str, intent: Dict[str, Any], result: List[Dict]) -> str:
        """Generate detailed explanation with actual results"""
        if not result:
            return self._generate_primary_explanation(sql, intent)
        
        base_explanation = self._generate_primary_explanation(sql, intent)
        
        # Add result-specific details
        details = []
        
        if intent.get("aggregation"):
            agg_type = intent["aggregation"]
            if result and len(result) > 0:
                # Get the aggregated value
                if isinstance(result[0], dict):
                    value = list(result[0].values())[0]
                    target = self._get_target_description(intent)
                    
                    if agg_type in self.explanation_patterns["aggregation"]:
                        detailed = self.explanation_patterns["aggregation"][agg_type]["detailed"]
                        details.append(detailed.format(target=target, value=value))
        
        elif intent.get("where_column"):
            # Count filtered results
            count = len(result)
            source = self._get_source_description(intent)
            details.append(f"The query returned {count} record{'s' if count != 1 else ''} from {source}")
        
        else:
            # General result count
            count = len(result)
            source = self._get_source_description(intent)
            details.append(f"Found {count} record{'s' if count != 1 else ''} in {source}")
        
        # Add sample data if result is not too large
        if result and len(result) <= 5:
            details.append("Sample results: " + str(result[:3]))
        
        return base_explanation + " " + " ".join(details)
    
    def _generate_natural_explanation(self, sql: str, intent: Dict[str, Any], result: List[Dict]) -> str:
        """Generate natural, conversational explanation"""
        if not result:
            return self._generate_primary_explanation(sql, intent)
        
        parts = []
        
        # Start with natural language opener
        if intent.get("aggregation"):
            agg_type = intent["aggregation"]
            target = self._get_target_description(intent)
            
            if agg_type in self.explanation_patterns["aggregation"] and result:
                value = list(result[0].values())[0]
                natural = self.explanation_patterns["aggregation"][agg_type]["natural"]
                parts.append(natural.format(target=target, value=value))
        
        elif intent.get("where_column"):
            count = len(result)
            source = self._get_source_description(intent)
            
            if count == 0:
                parts.append(f"No records found in {source} matching your criteria")
            elif count == 1:
                parts.append(f"Found 1 record in {source} that matches your criteria")
            else:
                parts.append(f"Found {count} records in {source} that match your criteria")
        
        else:
            count = len(result)
            source = self._get_source_description(intent)
            
            if count == 0:
                parts.append(f"No records found in {source}")
            elif count == 1:
                parts.append(f"Found 1 record in {source}")
            else:
                parts.append(f"Found {count} records in {source}")
        
        # Add contextual insights
        if intent.get("temporal"):
            temporal_info = intent["temporal"]
            if "time_range" in temporal_info:
                time_desc = temporal_info["time_range"].replace("_", " ")
                parts.append(f"This covers the {time_desc}")
        
        return " ".join(parts) + "."
    
    def _analyze_technical_details(self, sql: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical aspects of the generated query"""
        details = {
            "query_type": "SELECT",
            "complexity": "simple",
            "tables_used": [],
            "columns_used": [],
            "operations": [],
            "estimated_cost": "low"
        }
        
        # Analyze SQL structure
        if "JOIN" in sql.upper():
            details["query_type"] = "JOIN"
            details["complexity"] = "medium"
            details["operations"].append("join")
        
        if "GROUP BY" in sql.upper():
            details["operations"].append("aggregation")
            details["complexity"] = "medium"
        
        if "ORDER BY" in sql.upper():
            details["operations"].append("sorting")
        
        if "WHERE" in sql.upper():
            details["operations"].append("filtering")
        
        # Extract table names
        table_matches = re.findall(r'\b(FROM|JOIN)\s+(\w+)', sql, re.IGNORECASE)
        details["tables_used"] = [match[1] for match in table_matches]
        
        # Extract column names
        column_matches = re.findall(r'\b(\w+)\s*(?:,|FROM|WHERE|GROUP|ORDER|$)', sql, re.IGNORECASE)
        details["columns_used"] = [col for col in column_matches if col.upper() not in ['FROM', 'WHERE', 'GROUP', 'ORDER']]
        
        # Estimate complexity
        if len(details["tables_used"]) > 2 or len(details["operations"]) > 3:
            details["complexity"] = "high"
            details["estimated_cost"] = "medium"
        
        return details
    
    def _generate_insights(self, sql: str, intent: Dict[str, Any], result: List[Dict], 
                        execution_context: Dict[str, Any] = None) -> List[str]:
        """Generate intelligent insights about the query and results"""
        insights = []
        
        if not result:
            insights.append("No data was returned by this query")
            return insights
        
        # Performance insights
        if execution_context:
            exec_time = execution_context.get("execution_time", 0)
            if exec_time > 1.0:
                insights.append("This query took longer than expected to execute")
            elif exec_time < 0.1:
                insights.append("This query executed very quickly")
        
        # Data insights
        if len(result) > 1000:
            insights.append("Large result set returned - consider adding pagination")
        elif len(result) == 0:
            insights.append("No results found - check your query criteria")
        
        # Pattern insights
        if intent.get("aggregation"):
            agg_type = intent.get("aggregation")
            if agg_type == "COUNT" and len(result) == 1:
                count_val = list(result[0].values())[0]
                if isinstance(count_val, int) and count_val > 100:
                    insights.append(f"Large dataset detected: {count_val} records")
        
        # SQL pattern insights
        if "JOIN" in sql.upper() and len(result) < 10:
            insights.append("Join operation returned few results - verify join conditions")
        
        # Schema insights
        tables_used = self._extract_tables_from_sql(sql)
        if len(tables_used) > 1:
            insights.append(f"Multi-table query involving {len(tables_used)} tables")
        
        # AI enhancement insights
        if intent.get("ai_enhancements"):
            ai_info = intent["ai_enhancements"]
            if ai_info.get("nlu_method") == "transformer":
                insights.append("AI-powered natural language understanding was used")
            if ai_info.get("semantic_score", 0) > 0.8:
                insights.append("High confidence in semantic understanding")
        
        return insights
    
    def _analyze_confidence_factors(self, intent: Dict[str, Any], execution_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze factors affecting confidence"""
        factors = {
            "nlu_confidence": intent.get("confidence", 0.0),
            "query_complexity": "medium",
            "schema_match": "good",
            "ambiguity_level": "low",
            "overall_confidence": intent.get("confidence", 0.0)
        }
        
        # Analyze complexity
        if intent.get("tables") and len(intent["tables"]) > 2:
            factors["query_complexity"] = "high"
            factors["overall_confidence"] *= 0.9
        elif intent.get("tables") and len(intent["tables"]) == 1:
            factors["query_complexity"] = "low"
            factors["overall_confidence"] *= 1.1
        
        # Analyze ambiguity
        if not intent.get("table") or not intent.get("columns"):
            factors["ambiguity_level"] = "high"
            factors["overall_confidence"] *= 0.8
        elif intent.get("temporal") or intent.get("comparative"):
            factors["ambiguity_level"] = "medium"
            factors["overall_confidence"] *= 0.95
        
        # Analyze execution context
        if execution_context:
            if execution_context.get("optimizations_applied"):
                factors["overall_confidence"] *= 1.05
        
        # Ensure confidence stays in valid range
        factors["overall_confidence"] = max(0.0, min(1.0, factors["overall_confidence"]))
        
        return factors
    
    def _generate_execution_summary(self, execution_context: Dict[str, Any], result: List[Dict]) -> Dict[str, Any]:
        """Generate execution performance summary"""
        summary = {
            "execution_time": execution_context.get("execution_time", 0) if execution_context else 0,
            "rows_returned": len(result) if result else 0,
            "performance_score": execution_context.get("performance_score", 0) if execution_context else 0,
            "cache_hit": execution_context.get("cache_hit", False) if execution_context else False,
            "optimizations": execution_context.get("optimizations_applied", []) if execution_context else []
        }
        
        # Add performance assessment
        exec_time = summary["execution_time"]
        if exec_time < 0.1:
            summary["performance_rating"] = "excellent"
        elif exec_time < 0.5:
            summary["performance_rating"] = "good"
        elif exec_time < 2.0:
            summary["performance_rating"] = "fair"
        else:
            summary["performance_rating"] = "poor"
        
        return summary
    
    def _generate_suggestions(self, sql: str, intent: Dict[str, Any], result: List[Dict], 
                           execution_context: Dict[str, Any] = None) -> List[str]:
        """Generate intelligent suggestions for improvement"""
        suggestions = []
        
        # Performance suggestions
        if execution_context:
            exec_time = execution_context.get("execution_time", 0)
            if exec_time > 1.0:
                suggestions.append("Consider adding indexes to improve query performance")
                suggestions.append("This query might benefit from query optimization")
            
            if not execution_context.get("cache_hit") and exec_time > 0.5:
                suggestions.append("Frequent queries like this could benefit from caching")
        
        # Result suggestions
        if result:
            if len(result) > 1000:
                suggestions.append("Consider adding LIMIT clause for large result sets")
                suggestions.append("Implement pagination for better user experience")
            elif len(result) == 0:
                suggestions.append("Verify table names and column names in your question")
                suggestions.append("Try using broader search criteria")
        
        # Query structure suggestions
        if "SELECT *" in sql.upper():
            suggestions.append("Consider specifying only the columns you need instead of SELECT *")
        
        if "ORDER BY" not in sql.upper() and len(result) > 1:
            suggestions.append("Consider adding ORDER BY for consistent result ordering")
        
        # AI enhancement suggestions
        if intent.get("confidence", 1.0) < 0.7:
            suggestions.append("Try rephrasing your question with more specific terms")
            suggestions.append("Include table names in your question for better accuracy")
        
        # Security suggestions
        if execution_context and execution_context.get("security_blocked"):
            suggestions.append("Some operations were blocked for security reasons")
            suggestions.append("Contact administrator if you need elevated permissions")
        
        return suggestions
    
    def _get_target_description(self, intent: Dict[str, Any]) -> str:
        """Get human-readable description of target"""
        if intent.get("aggregation"):
            return intent["aggregation"].lower()
        elif intent.get("column"):
            return intent["column"]
        elif intent.get("columns") and intent["columns"]:
            return ", ".join(intent["columns"][:3])  # Limit to first 3 columns
        else:
            return "records"
    
    def _get_source_description(self, intent: Dict[str, Any]) -> str:
        """Get human-readable description of data source"""
        if intent.get("table"):
            return intent["table"]
        elif intent.get("tables") and intent["tables"]:
            return ", ".join(intent["tables"][:2])  # Limit to first 2 tables
        else:
            return "database"
    
    def _extract_tables_from_sql(self, sql: str) -> List[str]:
        """Extract table names from SQL query"""
        # Simple regex to extract table names
        tables = []
        
        # FROM clause
        from_matches = re.findall(r'\bFROM\s+(\w+)', sql, re.IGNORECASE)
        tables.extend(from_matches)
        
        # JOIN clauses
        join_matches = re.findall(r'\bJOIN\s+(\w+)', sql, re.IGNORECASE)
        tables.extend(join_matches)
        
        return list(set(tables))  # Remove duplicates
    
    def _log_explanation(self, explanation_data: Dict[str, Any]):
        """Log explanation for analytics and improvement"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "primary_explanation": explanation_data.get("primary_explanation"),
            "confidence": explanation_data.get("confidence_factors", {}).get("overall_confidence", 0),
            "insights_count": len(explanation_data.get("insights", [])),
            "suggestions_count": len(explanation_data.get("suggestions", []))
        }
        
        self.explanation_history.append(log_entry)
        
        # Keep history manageable
        if len(self.explanation_history) > 1000:
            self.explanation_history = self.explanation_history[-1000:]
        
        self.logger.info(f"Explanation generated with confidence: {explanation_data.get('confidence_factors', {}).get('overall_confidence', 0):.2f}")
    
    def get_explanation_statistics(self) -> Dict[str, Any]:
        """Get explanation generation statistics"""
        total_explanations = len(self.explanation_history)
        
        if total_explanations == 0:
            return {
                "total_explanations": 0,
                "average_confidence": 0,
                "most_common_insights": [],
                "explanation_history_size": 0
            }
        
        avg_confidence = sum(exp.get("confidence", 0) for exp in self.explanation_history) / total_explanations
        
        # Collect all insights from history
        all_insights = []
        for exp in self.explanation_history:
            # This would need to be enhanced to store insights in history
            pass
        
        return {
            "total_explanations": total_explanations,
            "average_confidence": avg_confidence,
            "most_common_insights": all_insights[:10],  # Would need proper implementation
            "explanation_history_size": len(self.explanation_history)
        }

# Backward compatibility alias
ExplanationAgent = EnhancedExplanationAgent
