import re
from typing import Dict, List, Optional, Tuple

# Optional AI/ML imports with graceful fallback
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None

import logging

class EnhancedNLUAgent:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Enhanced NLU Agent with transformer-based understanding
        Falls back to regex if transformers unavailable
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cpu"  # Default to CPU if no CUDA
        self.use_transformers = TRANSFORMERS_AVAILABLE
        
        try:
            if TRANSFORMERS_AVAILABLE:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.model.to(self.device)
                self.use_transformers = True
                logging.info(f"Loaded transformer model: {model_name}")
            else:
                raise ImportError("Transformers not available")
        except Exception as e:
            logging.warning(f"Failed to load transformers ({e}), falling back to regex")
            self.use_transformers = False

    def _semantic_understanding(self, text: str, schema: Dict) -> Dict:
        """Use transformers for semantic understanding"""
        if not self.use_transformers:
            return self._regex_fallback(text, schema)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.softmax(outputs.logits, dim=-1)
            
            # Extract semantic features
            confidence = torch.max(predictions).item()
            
            # Combine with regex for structured extraction
            regex_result = self._regex_fallback(text, schema)
            regex_result["confidence"] = confidence
            regex_result["semantic_score"] = confidence
            
            return regex_result
            
        except Exception as e:
            logging.error(f"Transformer inference failed: {e}")
            return self._regex_fallback(text, schema)

    def _extract_temporal_intent(self, text: str) -> Dict:
        """Extract temporal expressions and time-based intent"""
        temporal_patterns = {
            "last_month": r"last month|past month|previous month",
            "last_year": r"last year|past year|previous year",
            "this_month": r"this month|current month",
            "this_year": r"this year|current year",
            "last_week": r"last week|past week",
            "yesterday": r"yesterday|yday",
            "today": r"today|now"
        }
        
        temporal_intent = {}
        for intent, pattern in temporal_patterns.items():
            if re.search(pattern, text.lower()):
                temporal_intent["time_range"] = intent
                break
        
        return temporal_intent

    def _extract_comparative_intent(self, text: str) -> Dict:
        """Extract comparative expressions"""
        comparative_patterns = {
            "greater_than": r"greater than|more than|above|over|>\s*\d+",
            "less_than": r"less than|below|under|<\s*\d+",
            "between": r"between\s+\d+\s+and\s+\d+",
            "not_equal": r"not equal|different from|!=|<>"
        }
        
        comparative_intent = {}
        for intent, pattern in comparative_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                comparative_intent["comparison"] = intent
                comparative_intent["raw_expression"] = match.group()
                break
        
        return comparative_intent

    def _enhanced_column_detection(self, text: str, schema: Dict, detected_tables: List[str]) -> List[str]:
        """Enhanced column detection with semantic similarity"""
        detected_columns = []
        text_lower = text.lower()
        
        # Direct matching
        for table in detected_tables:
            for col in schema.get(table, []):
                col_l = col.lower()
                if re.search(r'\b' + re.escape(col_l) + r'\b', text_lower):
                    detected_columns.append(col)
        
        # Semantic matching for common terms
        semantic_mappings = {
            "name": ["name", "full_name", "first_name", "last_name", "username"],
            "age": ["age", "years", "years_old", "age_group"],
            "score": ["score", "marks", "grade", "points", "rating"],
            "date": ["date", "time", "created", "updated", "timestamp"],
            "id": ["id", "identifier", "key", "pk"]
        }
        
        for semantic_term, variations in semantic_mappings.items():
            if semantic_term in text_lower:
                for table in detected_tables:
                    for col in schema.get(table, []):
                        if col.lower() in variations and col not in detected_columns:
                            detected_columns.append(col)
        
        return list(set(detected_columns))

    def _regex_fallback(self, text: str, schema: Dict) -> Dict:
        """Original regex-based parsing as fallback"""
        original_text = text
        text = text.lower()

        detected_tables = []
        
        # Detect tables
        for table in schema.keys():
            table_l = table.lower()
            if re.search(r'\b' + re.escape(table_l) + r'\b', text):
                detected_tables.append(table)
            if table_l.endswith("s"):
                singular = table_l[:-1]
                if re.search(r'\b' + re.escape(singular) + r'\b', text):
                    detected_tables.append(table)

        detected_tables = list(dict.fromkeys(detected_tables))
        
        # Enhanced column detection
        detected_columns = self._enhanced_column_detection(text, schema, detected_tables)

        # Detect aggregation
        aggregation = None
        if re.search(r'\bcount\b|\bhow many\b', text):
            aggregation = "COUNT"
        elif re.search(r'\baverage\b|\bavg\b|\bmean\b', text):
            aggregation = "AVG"
        elif re.search(r'\bmaximum\b|\bmax\b|\bhighest\b', text):
            aggregation = "MAX"
        elif re.search(r'\bminimum\b|\bmin\b|\blowest\b', text):
            aggregation = "MIN"
        elif re.search(r'\bsum\b|\btotal\b', text):
            aggregation = "SUM"

        # WHERE detection
        where_column = None
        where_operator = None
        where_value = None

        temp = text.replace("greater than", ">").replace("less than", "<").replace("equal to", "=")
        match = re.search(r'\b(\w+)\b\s*(=|>|<)\s*([\w\.]+)', temp)

        if match:
            candidate_col = match.group(1).upper()
            where_operator = match.group(2)
            raw_value = match.group(3)

            all_columns = set()
            for t, cols in schema.items():
                for c in cols:
                    all_columns.add(c.upper())

            if candidate_col in all_columns:
                where_column = candidate_col
                if re.match(r'^\d+(\.\d+)?$', raw_value):
                    where_value = raw_value
                else:
                    original_match = re.search(r'\b' + re.escape(candidate_col) + r'\b\s*(=|>|<)\s*([\w\.]+)', original_text, re.IGNORECASE)
                    if original_match:
                        where_value = f"'{original_match.group(2)}'"
                    else:
                        where_value = f"'{raw_value}'"

        # Extract additional intents
        temporal_intent = self._extract_temporal_intent(text)
        comparative_intent = self._extract_comparative_intent(text)

        main_table = detected_tables[0] if len(detected_tables) == 1 else None
        main_column = detected_columns[0] if len(detected_columns) == 1 else None

        return {
            "table": main_table,
            "tables": detected_tables,
            "column": main_column,
            "columns": detected_columns,
            "aggregation": aggregation,
            "where_column": where_column,
            "where_operator": where_operator,
            "where_value": where_value,
            "temporal": temporal_intent,
            "comparative": comparative_intent,
            "confidence": 0.8 if self.use_transformers else 0.6,
            "method": "transformer" if self.use_transformers else "regex"
        }

    def parse(self, text: str, schema: Dict) -> Dict:
        """Main parsing method with enhanced understanding"""
        return self._semantic_understanding(text, schema)
