"""
Enhanced Reflex Agent for NeuroSQL v2.0
Advanced error correction with ML-based learning and pattern recognition
"""

import re
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from collections import defaultdict

class EnhancedReflexAgent:
    """Enhanced reflex agent with intelligent error correction and learning capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.correction_history = []
        self.error_patterns = defaultdict(int)
        self.success_patterns = defaultdict(int)
        self.correction_rules = self._load_correction_rules()
        self.learning_enabled = True
        
    def _load_correction_rules(self) -> Dict[str, Dict]:
        """Load comprehensive correction rules"""
        return {
            "column_mapping": {
                # Common column name variations
                "score": ["marks", "grade", "points", "rating"],
                "name": ["full_name", "student_name", "person_name"],
                "age": ["student_age", "years", "age_group"],
                "id": ["student_id", "user_id", "identifier", "pk"],
                "date": ["created_date", "timestamp", "time", "created_at"],
                "department": ["dept", "faculty", "division", "college"],
                "email": ["email_address", "mail", "contact_email"]
            },
            "table_mapping": {
                # Common table name variations
                "student": ["students", "pupils", "learners"],
                "course": ["courses", "subjects", "classes"],
                "enrollment": ["enrollments", "registrations", "signups"],
                "instructor": ["instructors", "teachers", "professors", "staff"],
                "department": ["departments", "depts", "faculties"]
            },
            "function_mapping": {
                # SQL function corrections
                "avg": ["average", "mean"],
                "count": ["total", "number", "quantity"],
                "max": ["maximum", "highest"],
                "min": ["minimum", "lowest"],
                "sum": ["total", "addition"]
            }
        }
    
    def correct_query(self, sql: str, error_message: str, schema: Dict[str, List[str]], 
                   database: str = "default") -> Tuple[str, Dict[str, Any]]:
        """
        Enhanced query correction with multiple strategies
        
        Args:
            sql: Original SQL query that failed
            error_message: Error message from database
            schema: Database schema for validation
            database: Database name for context
            
        Returns:
            Tuple of (corrected_sql, correction_info)
        """
        correction_info = {
            "original_sql": sql,
            "error_message": error_message,
            "corrections_applied": [],
            "confidence": 0.0,
            "strategy": None,
            "execution_time": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Strategy 1: Pattern-based error correction
            corrected_sql, pattern_corrections = self._pattern_based_correction(sql, error_message, schema)
            if corrected_sql != sql:
                correction_info["corrections_applied"].extend(pattern_corrections)
                correction_info["strategy"] = "pattern_based"
            
            # Strategy 2: Schema-based correction
            if corrected_sql == sql:  # Only if pattern correction didn't work
                corrected_sql, schema_corrections = self._schema_based_correction(corrected_sql, error_message, schema)
                if corrected_sql != sql:
                    correction_info["corrections_applied"].extend(schema_corrections)
                    correction_info["strategy"] = "schema_based"
            
            # Strategy 3: Learning-based correction
            if self.learning_enabled and corrected_sql == sql:
                corrected_sql, learning_corrections = self._learning_based_correction(corrected_sql, error_message)
                if corrected_sql != sql:
                    correction_info["corrections_applied"].extend(learning_corrections)
                    if correction_info["strategy"]:
                        correction_info["strategy"] += "_learning"
                    else:
                        correction_info["strategy"] = "learning_based"
            
            # Strategy 4: Fallback intelligent correction
            if corrected_sql == sql:
                corrected_sql, fallback_corrections = self._fallback_correction(corrected_sql, error_message, schema)
                if corrected_sql != sql:
                    correction_info["corrections_applied"].extend(fallback_corrections)
                    if correction_info["strategy"]:
                        correction_info["strategy"] += "_fallback"
                    else:
                        correction_info["strategy"] = "fallback"
            
            # Calculate confidence based on correction strategy
            correction_info["confidence"] = self._calculate_correction_confidence(correction_info)
            correction_info["corrected_sql"] = corrected_sql
            correction_info["execution_time"] = time.time() - start_time
            
            # Log correction for learning
            self._log_correction(correction_info)
            
            return corrected_sql, correction_info
            
        except Exception as e:
            self.logger.error(f"Reflex correction error: {e}")
            correction_info["strategy"] = "failed"
            correction_info["execution_time"] = time.time() - start_time
            return sql, correction_info
    
    def _pattern_based_correction(self, sql: str, error_message: str, schema: Dict[str, List[str]]) -> Tuple[str, List[str]]:
        """Pattern-based error correction using regex and common error patterns"""
        corrected_sql = sql
        corrections = []
        
        # Error: No such table
        if "no such table" in error_message.lower():
            table_match = re.search(r"no such table: (\w+)", error_message.lower())
            if table_match:
                invalid_table = table_match.group(1)
                suggested_table = self._suggest_table_correction(invalid_table, schema)
                if suggested_table and suggested_table != invalid_table:
                    corrected_sql = re.sub(rf'\b{re.escape(invalid_table)}\b', suggested_table, corrected_sql, flags=re.IGNORECASE)
                    corrections.append(f"Table '{invalid_table}' -> '{suggested_table}'")
        
        # Error: No such column
        elif "no such column" in error_message.lower():
            column_match = re.search(r"no such column: (\w+)", error_message.lower())
            if column_match:
                invalid_column = column_match.group(1)
                suggested_column = self._suggest_column_correction(invalid_column, schema)
                if suggested_column and suggested_column != invalid_column:
                    corrected_sql = re.sub(rf'\b{re.escape(invalid_column)}\b', suggested_column, corrected_sql, flags=re.IGNORECASE)
                    corrections.append(f"Column '{invalid_column}' -> '{suggested_column}'")
        
        # Error: Ambiguous column
        elif "ambiguous column name" in error_message.lower():
            # Find ambiguous columns and qualify them with table names
            tables_in_query = re.findall(r'\b(FROM|JOIN)\s+(\w+)', sql, re.IGNORECASE)
            if tables_in_query:
                for table in tables_in_query[1:]:  # Skip FROM, get table names
                    if table in schema:
                        columns = schema[table]
                        for col in columns:
                            if col in sql and '.' not in sql.split(col)[0]:
                                corrected_sql = re.sub(rf'\b{re.escape(col)}\b', f'{table}.{col}', corrected_sql)
                                corrections.append(f"Qualified column: {col} -> {table}.{col}")
        
        # Error: Syntax error near
        elif "syntax error" in error_message.lower():
            # Common syntax fixes
            syntax_corrections = self._fix_syntax_errors(sql, error_message)
            if syntax_corrections:
                corrected_sql = syntax_corrections[0]  # Take first suggestion
                corrections.extend(syntax_corrections[1:])
        
        return corrected_sql, corrections
    
    def _schema_based_correction(self, sql: str, error_message: str, schema: Dict[str, List[str]]) -> Tuple[str, List[str]]:
        """Schema-based correction using database schema information"""
        corrected_sql = sql
        corrections = []
        
        # Extract table and column references from SQL
        tables_in_sql = set(re.findall(r'\b(\w+)\b', sql))
        columns_in_sql = set(re.findall(r'\b(\w+)\b', sql))
        
        # Check table validity
        all_tables = set(schema.keys())
        for table in tables_in_sql:
            if table not in all_tables:
                suggested_table = self._find_closest_match(table, all_tables)
                if suggested_table:
                    corrected_sql = re.sub(rf'\b{re.escape(table)}\b', suggested_table, corrected_sql, flags=re.IGNORECASE)
                    corrections.append(f"Table '{table}' -> '{suggested_table}' (schema match)")
        
        # Check column validity
        all_columns = set()
        for table_cols in schema.values():
            all_columns.update(table_cols)
        
        for column in columns_in_sql:
            if column not in all_columns:
                suggested_column = self._find_closest_match(column, all_columns)
                if suggested_column:
                    corrected_sql = re.sub(rf'\b{re.escape(column)}\b', suggested_column, corrected_sql, flags=re.IGNORECASE)
                    corrections.append(f"Column '{column}' -> '{suggested_column}' (schema match)")
        
        return corrected_sql, corrections
    
    def _learning_based_correction(self, sql: str, error_message: str) -> Tuple[str, List[str]]:
        """Learning-based correction using historical correction patterns"""
        corrected_sql = sql
        corrections = []
        
        # Find similar past corrections
        error_pattern = self._extract_error_pattern(error_message)
        
        if error_pattern in self.error_patterns:
            # Look for successful corrections for similar errors
            similar_corrections = [
                correction for correction in self.correction_history
                if correction["error_pattern"] == error_pattern and correction["success"]
            ]
            
            if similar_corrections:
                # Use the most recent successful correction
                best_correction = max(similar_corrections, key=lambda x: x["timestamp"])
                corrected_sql = best_correction["corrected_sql"]
                corrections.append(f"Applied learned correction from {best_correction['timestamp']}")
        
        return corrected_sql, corrections
    
    def _fallback_correction(self, sql: str, error_message: str, schema: Dict[str, List[str]]) -> Tuple[str, List[str]]:
        """Fallback intelligent correction when other strategies fail"""
        corrected_sql = sql
        corrections = []
        
        # Try to identify and fix common issues
        
        # Fix missing quotes around string literals
        if "unrecognized token" in error_message.lower():
            # Find unquoted string values and add quotes
            unquoted_strings = re.findall(r'=\s*(\w+)\s*(?:WHERE|AND|OR|$)', sql)
            for unquoted in unquoted_strings:
                if unquoted.isalpha():  # Likely a string that needs quotes
                    corrected_sql = re.sub(rf'=\s*{re.escape(unquoted)}\s*', f"= '{unquoted}'", corrected_sql)
                    corrections.append(f"Added quotes to '{unquoted}'")
        
        # Fix missing table aliases in joins
        if "ambiguous" in error_message.lower() and "JOIN" in sql.upper():
            # Add table prefixes to ambiguous columns
            tables = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', sql, re.IGNORECASE)
            if len(tables) > 1:
                for i, table in enumerate(tables):
                    if table:  # Skip empty matches
                        # Simple heuristic: prefix columns with table name
                        pattern = rf'\b(\w+)\b(?=\s*(?:WHERE|AND|OR|ORDER|GROUP|$))'
                        matches = re.findall(pattern, sql)
                        for match in matches:
                            if match not in tables:  # Column not already qualified
                                corrected_sql = re.sub(rf'\b{re.escape(match)}\b', f'{table}.{match}', corrected_sql)
                                corrections.append(f"Qualified column '{match}' with table '{table}'")
        
        # Fix aggregation function syntax
        if "misuse" in error_message.lower() and "aggregate" in error_message.lower():
            # Fix common aggregation issues
            corrected_sql, agg_corrections = self._fix_aggregation_errors(sql)
            corrections.extend(agg_corrections)
        
        return corrected_sql, corrections
    
    def _suggest_table_correction(self, invalid_table: str, schema: Dict[str, List[str]]) -> Optional[str]:
        """Suggest correction for invalid table name"""
        # Check mapping rules first
        for correct_name, variations in self.correction_rules["table_mapping"].items():
            if invalid_table.lower() in [v.lower() for v in variations]:
                return correct_name
        
        # Check for exact matches with different case
        for table_name in schema.keys():
            if table_name.lower() == invalid_table.lower():
                return table_name
        
        # Check for close matches (edit distance)
        return self._find_closest_match(invalid_table, schema.keys())
    
    def _suggest_column_correction(self, invalid_column: str, schema: Dict[str, List[str]]) -> Optional[str]:
        """Suggest correction for invalid column name"""
        # Check mapping rules first
        for correct_name, variations in self.correction_rules["column_mapping"].items():
            if invalid_column.lower() in [v.lower() for v in variations]:
                return correct_name
        
        # Check all columns in schema
        all_columns = set()
        for table_cols in schema.values():
            all_columns.update(table_cols)
        
        return self._find_closest_match(invalid_column, all_columns)
    
    def _find_closest_match(self, invalid_name: str, valid_names: List[str]) -> Optional[str]:
        """Find closest match using simple string similarity"""
        if not valid_names:
            return None
        
        invalid_lower = invalid_name.lower()
        
        # Exact match with different case
        for name in valid_names:
            if name.lower() == invalid_lower:
                return name
        
        # Check for substring matches
        for name in valid_names:
            if invalid_lower in name.lower() or name.lower() in invalid_lower:
                return name
        
        # Simple edit distance (character-level similarity)
        best_match = None
        best_score = 0
        
        for name in valid_names:
            score = self._calculate_similarity(invalid_lower, name.lower())
            if score > best_score and score > 0.6:  # 60% similarity threshold
                best_score = score
                best_match = name
        
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity"""
        # Levenshtein distance approximation
        if str1 == str2:
            return 1.0
        
        # Common prefix/suffix
        common_prefix = 0
        for i in range(min(len(str1), len(str2))):
            if str1[i] == str2[i]:
                common_prefix += 1
            else:
                break
        
        common_suffix = 0
        for i in range(1, min(len(str1), len(str2)) + 1):
            if str1[-i] == str2[-i]:
                common_suffix += 1
            else:
                break
        
        # Combined similarity score
        max_len = max(len(str1), len(str2))
        similarity = (common_prefix + common_suffix) / max_len
        
        return similarity
    
    def _fix_syntax_errors(self, sql: str, error_message: str) -> List[str]:
        """Fix common SQL syntax errors"""
        corrections = []
        corrected_sql = sql
        
        # Fix missing commas in SELECT lists
        if re.search(r'SELECT\s+\w+\s+\w+\s+FROM', sql, re.IGNORECASE):
            corrected_sql = re.sub(r'(SELECT\s+\w+)\s+(\w+)(\s+FROM)', r'\1, \2\3', corrected_sql)
            corrections.append("Added missing comma in SELECT list")
        
        # Fix missing GROUP BY for aggregations
        if "aggregate" in error_message.lower() and "GROUP BY" not in sql.upper():
            agg_functions = re.findall(r'(COUNT|SUM|AVG|MAX|MIN)\s*\(', sql, re.IGNORECASE)
            if agg_functions:
                # Simple heuristic: add GROUP BY for non-aggregated columns
                select_cols = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE)
                if select_cols:
                    cols = [col.strip() for col in select_cols.group(1).split(',')]
                    non_agg_cols = [col for col in cols if not any(agg in col.upper() for agg in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])]
                    if non_agg_cols:
                        corrected_sql += f" GROUP BY {non_agg_cols[0]}"
                        corrections.append(f"Added GROUP BY {non_agg_cols[0]}")
        
        # Fix missing quotes in string comparisons
        if re.search(r'=\s*\w+\s*(?:WHERE|AND|OR)', sql):
            string_vars = re.findall(r'=\s*(\w+)\s*(?:WHERE|AND|OR)', sql)
            for var in string_vars:
                if var.isalpha():  # Likely a string variable
                    corrected_sql = re.sub(rf'=\s*{re.escape(var)}\s', f"= '{var}' ", corrected_sql)
                    corrections.append(f"Added quotes to string variable '{var}'")
        
        return [corrected_sql] + corrections
    
    def _fix_aggregation_errors(self, sql: str) -> Tuple[str, List[str]]:
        """Fix common aggregation function errors"""
        corrected_sql = sql
        corrections = []
        
        # Fix COUNT(*) vs COUNT(column)
        if "COUNT(" in sql.upper() and "GROUP BY" in sql.upper():
            # Check if we're using COUNT(*) with GROUP BY
            if "COUNT(*)" in sql.upper():
                # Try to find a non-aggregated column to use
                select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE)
                if select_match:
                    cols = [col.strip() for col in select_match.group(1).split(',')]
                    non_agg_cols = [col for col in cols if not any(agg in col.upper() for agg in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])]
                    if non_agg_cols:
                        corrected_sql = corrected_sql.replace("COUNT(*)", f"COUNT({non_agg_cols[0]})")
                        corrections.append(f"Changed COUNT(*) to COUNT({non_agg_cols[0]})")
        
        # Fix AVG without GROUP BY
        if "AVG(" in sql.upper() and "GROUP BY" not in sql.upper():
            select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE)
            if select_match:
                cols = [col.strip() for col in select_match.group(1).split(',')]
                non_agg_cols = [col for col in cols if not any(agg in col.upper() for agg in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])]
                if non_agg_cols:
                    corrected_sql += f" GROUP BY {non_agg_cols[0]}"
                    corrections.append(f"Added GROUP BY {non_agg_cols[0]} for AVG function")
        
        return corrected_sql, corrections
    
    def _extract_error_pattern(self, error_message: str) -> str:
        """Extract normalized error pattern for learning"""
        # Normalize error message for pattern matching
        pattern = error_message.lower()
        
        # Remove specific values and keep structure
        pattern = re.sub(r"'[^']*'", "'X'", pattern)  # Replace quoted values
        pattern = re.sub(r'\b\d+\b', 'N', pattern)  # Replace numbers
        pattern = re.sub(r'\b\w+\.\w+\b', 'table.column', pattern)  # Replace table.column
        
        return pattern
    
    def _calculate_correction_confidence(self, correction_info: Dict) -> float:
        """Calculate confidence score for correction"""
        base_confidence = 0.5
        
        # Strategy-based confidence
        strategy = correction_info.get("strategy", "")
        if "pattern_based" in strategy:
            base_confidence = 0.8
        elif "schema_based" in strategy:
            base_confidence = 0.9
        elif "learning_based" in strategy:
            base_confidence = 0.7  # Learning needs validation
        elif "fallback" in strategy:
            base_confidence = 0.6
        
        # Adjust based on number of corrections
        num_corrections = len(correction_info.get("corrections_applied", []))
        if num_corrections == 0:
            return 0.0  # No corrections made
        elif num_corrections == 1:
            base_confidence += 0.1
        elif num_corrections > 3:
            base_confidence -= 0.2  # Many corrections suggest lower confidence
        
        # Adjust based on execution time
        execution_time = correction_info.get("execution_time", 0)
        if execution_time > 1.0:  # Slow correction
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def _log_correction(self, correction_info: Dict):
        """Log correction for learning and analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_sql": correction_info.get("original_sql"),
            "corrected_sql": correction_info.get("corrected_sql"),
            "error_message": correction_info.get("error_message"),
            "strategy": correction_info.get("strategy"),
            "corrections_applied": correction_info.get("corrections_applied"),
            "confidence": correction_info.get("confidence"),
            "execution_time": correction_info.get("execution_time")
        }
        
        self.correction_history.append(log_entry)
        
        # Update error patterns for learning
        error_pattern = self._extract_error_pattern(correction_info.get("error_message", ""))
        if correction_info.get("corrected_sql") != correction_info.get("original_sql"):
            self.success_patterns[error_pattern] += 1
        else:
            self.error_patterns[error_pattern] += 1
        
        # Keep history manageable
        if len(self.correction_history) > 1000:
            self.correction_history = self.correction_history[-1000:]
        
        self.logger.info(f"Reflex correction applied: {correction_info['strategy']} with confidence {correction_info['confidence']:.2f}")
    
    def get_correction_statistics(self) -> Dict[str, Any]:
        """Get correction and learning statistics"""
        total_corrections = len(self.correction_history)
        successful_corrections = sum(1 for c in self.correction_history if c.get("corrected_sql") != c.get("original_sql"))
        
        strategy_counts = {}
        for correction in self.correction_history:
            strategy = correction.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_corrections": total_corrections,
            "successful_corrections": successful_corrections,
            "success_rate": (successful_corrections / total_corrections * 100) if total_corrections > 0 else 0,
            "strategy_distribution": strategy_counts,
            "common_error_patterns": dict(self.error_patterns.most_common(10)),
            "learning_enabled": self.learning_enabled,
            "correction_history_size": len(self.correction_history)
        }
    
    def enable_learning(self, enabled: bool = True):
        """Enable or disable learning-based corrections"""
        self.learning_enabled = enabled
        self.logger.info(f"Reflex learning {'enabled' if enabled else 'disabled'}")
    
    def clear_correction_history(self):
        """Clear correction history and reset learning"""
        self.correction_history.clear()
        self.error_patterns.clear()
        self.success_patterns.clear()
        self.logger.info("Reflex correction history cleared")

# Backward compatibility alias
ReflexAgent = EnhancedReflexAgent
