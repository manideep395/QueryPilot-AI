import random

class SQLPlannerAgent:

    # =========================
    # Helper: find column that contains value
    # =========================
    def find_column_for_value(self, conn, tables, schema, value):
        raw_value = value.strip("'")

        cursor = conn.cursor()

        for table in tables:
            for col in schema.get(table, []):
                try:
                    q = f"SELECT 1 FROM {table} WHERE {col} = ? LIMIT 1"
                    cursor.execute(q, (raw_value,))
                    if cursor.fetchone():
                        return table, col
                except:
                    pass

        return None, None

    # =========================
    # Main SQL generator (SAFE)
    # =========================
    def generate_sql(self, intent, schema, relations, conn):

        tables = intent.get("tables") or []
        main_table = intent.get("table")
        columns = intent.get("columns") or []
        aggregation = intent.get("aggregation")

        where_column = intent.get("where_column")
        where_operator = intent.get("where_operator")
        where_value = intent.get("where_value")

        # =========================
        # HARD BLOCK: No table
        # =========================
        if not tables and not main_table:
            return None

        # Normalize tables
        if not tables:
            tables = [main_table]

        # =========================
        # Validate tables exist
        # =========================
        for t in tables:
            if t not in schema:
                return None

        # =========================
        # Validate columns exist
        # =========================
        for c in columns:
            if not any(c in schema[t] for t in tables):
                return None

        # =========================
        # WHERE validation
        # =========================
        if where_column:
            if not any(where_column in schema[t] for t in tables):
                # Try auto-fix using value lookup
                new_table, new_col = self.find_column_for_value(conn, tables, schema, where_value or "")
                if new_col:
                    print(f"⚠️ Auto-corrected WHERE column: {where_column} → {new_col}")
                    where_column = new_col
                else:
                    return None

        # =========================
        # CASE 1: SINGLE TABLE
        # =========================
        if len(tables) == 1:
            table = tables[0]

            # SELECT part
            if aggregation:
                if columns:
                    select_part = f"{aggregation}({columns[0]})"
                else:
                    select_part = f"{aggregation}(*)"
            else:
                if columns:
                    select_part = ", ".join(columns)
                else:
                    select_part = "*"

            sql = f"SELECT {select_part} FROM {table}"

            # WHERE
            if where_column and where_operator and where_value:
                sql += f" WHERE {where_column} {where_operator} {where_value}"

            return sql

        # =========================
        # CASE 2: TWO TABLE JOIN
        # =========================
        if len(tables) == 2:
            t1, t2 = tables

            join_condition = None

            for rel in relations:
                if rel["from_table"] == t1 and rel["to_table"] == t2:
                    join_condition = f"{t1}.{rel['from_column']} = {t2}.{rel['to_column']}"
                elif rel["from_table"] == t2 and rel["to_table"] == t1:
                    join_condition = f"{t2}.{rel['from_column']} = {t1}.{rel['to_column']}"

            # ❌ No relation → refuse
            if join_condition is None:
                return None

            # SELECT columns
            select_cols = []

            if columns:
                for col in columns:
                    if col in schema[t1]:
                        select_cols.append(f"{t1}.{col}")
                    elif col in schema[t2]:
                        select_cols.append(f"{t2}.{col}")
                    else:
                        return None
            else:
                select_cols.append(f"{t1}.*")
                select_cols.append(f"{t2}.*")

            select_part = ", ".join(select_cols)

            sql = f"""
SELECT {select_part}
FROM {t1}
JOIN {t2} ON {join_condition}
""".strip()

            # WHERE
            if where_column and where_operator and where_value:
                if where_column in schema[t1]:
                    sql += f"\nWHERE {t1}.{where_column} {where_operator} {where_value}"
                elif where_column in schema[t2]:
                    sql += f"\nWHERE {t2}.{where_column} {where_operator} {where_value}"
                else:
                    return None

            return sql

        # =========================
        # ❌ MORE THAN 2 TABLES NOT SUPPORTED
        # =========================
        return None