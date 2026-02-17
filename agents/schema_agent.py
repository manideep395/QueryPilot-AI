import sqlite3
class SchemaAgent:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        schema = {}
        foreign_keys = []

        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for (table_name,) in tables:
            # Columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            schema[table_name] = columns

            # Foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fk_info = cursor.fetchall()
            for fk in fk_info:
                foreign_keys.append({
                    "from_table": table_name,
                    "from_column": fk[3],
                    "to_table": fk[2],
                    "to_column": fk[4]
                })

        conn.close()

        return {
            "tables": schema,
            "relations": foreign_keys
        }