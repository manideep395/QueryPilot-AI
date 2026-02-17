import re

class NLUAgent:
    def parse(self, text, schema):
        original_text = text
        text = text.lower()

        detected_tables = []
        detected_columns = []

        # =========================
        # 1. Detect tables (STRICT)
        # =========================
        for table in schema.keys():
            table_l = table.lower()

            # Match full word only
            if re.search(r'\b' + re.escape(table_l) + r'\b', text):
                detected_tables.append(table)

            # Also allow simple singular form (STUDENT vs students)
            if table_l.endswith("s"):
                singular = table_l[:-1]
                if re.search(r'\b' + re.escape(singular) + r'\b', text):
                    detected_tables.append(table)

        # Deduplicate
        detected_tables = list(dict.fromkeys(detected_tables))

        # =========================
        # 2. Detect columns (ONLY from detected tables)
        # =========================
        for table in detected_tables:
            for col in schema[table]:
                col_l = col.lower()
                if re.search(r'\b' + re.escape(col_l) + r'\b', text):
                    detected_columns.append(col)

        # Deduplicate
        detected_columns = list(dict.fromkeys(detected_columns))

        # =========================
        # 3. Detect aggregation (STRICT)
        # =========================
        aggregation = None
        if re.search(r'\bcount\b|\bhow many\b', text):
            aggregation = "COUNT"
        elif re.search(r'\baverage\b|\bavg\b', text):
            aggregation = "AVG"
        elif re.search(r'\bmaximum\b|\bmax\b', text):
            aggregation = "MAX"
        elif re.search(r'\bminimum\b|\bmin\b', text):
            aggregation = "MIN"

        # =========================
        # 4. WHERE detection (STRICT)
        # =========================
        where_column = None
        where_operator = None
        where_value = None

        # Normalize operators
        temp = text.replace("greater than", ">").replace("less than", "<").replace("equal to", "=")

        # Only allow simple patterns: col > value, col = value, col < value
        match = re.search(r'\b(\w+)\b\s*(=|>|<)\s*([\w\.]+)', temp)

        if match:
            candidate_col = match.group(1).upper()
            where_operator = match.group(2)
            raw_value = match.group(3)

            # Check that column exists in schema (any table)
            all_columns = set()
            for t, cols in schema.items():
                for c in cols:
                    all_columns.add(c.upper())

            if candidate_col in all_columns:
                where_column = candidate_col

                # If numeric → keep as is
                if re.match(r'^\d+(\.\d+)?$', raw_value):
                    where_value = raw_value
                else:
                    # Recover original casing from original text
                    original_match = re.search(r'\b' + re.escape(candidate_col) + r'\b\s*(=|>|<)\s*([\w\.]+)', original_text, re.IGNORECASE)
                    if original_match:
                        real_value = original_match.group(2)
                        where_value = f"'{original_match.group(2)}'"
                    else:
                        where_value = f"'{raw_value}'"

        # =========================
        # 5. Choose main table (ONLY if exactly one)
        # =========================
        main_table = detected_tables[0] if len(detected_tables) == 1 else None

        # =========================
        # 6. Choose main column (ONLY if exactly one)
        # =========================
        main_column = detected_columns[0] if len(detected_columns) == 1 else None

        # =========================
        # 7. FINAL SAFE INTENT
        # =========================
        return {
            "table": main_table,
            "tables": detected_tables,      # may be []
            "column": main_column,
            "columns": detected_columns,    # may be []
            "aggregation": aggregation,

            "where_column": where_column,
            "where_operator": where_operator,
            "where_value": where_value
        }