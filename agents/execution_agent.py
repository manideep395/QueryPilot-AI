import sqlite3
import csv
from rich.table import Table
from rich.console import Console

console = Console()

class ExecutionAgent:
    
    # =========================
    # Import CSV as table
    # =========================
    def import_csv(self, conn, csv_path, table_name):
        cursor = conn.cursor()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

            # Create table
            columns = ", ".join([f"{h} TEXT" for h in headers])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

            # Insert rows
            for row in reader:
                placeholders = ",".join(["?"] * len(row))
                cursor.execute(
                    f"INSERT INTO {table_name} VALUES ({placeholders})", row
                )

        conn.commit()
        print(f"✅ Imported {csv_path} as table {table_name}")
    # =========================
    # Show tables
    # =========================
    def show_tables(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        table = Table(title="Tables in Database")
        table.add_column("Table Name")

        for t in tables:
            table.add_row(t)

        console.print(table)
        return tables
    # =========================
    # Describe table
    # =========================
    def describe_table(self, conn, table_name):
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()

        if not rows:
            print(f"❌ Table '{table_name}' not found.")
            return None

        table = Table(title=f"Schema of {table_name}")
        table.add_column("Column")
        table.add_column("Type")

        for row in rows:
            table.add_row(row[1], row[2])

        console.print(table)
        return rows
    def __init__(self):
        pass   # ✅ No db_path anymore

    # =========================
    # Execute SQL using given connection
    # =========================
    def execute(self, sql, conn):
        try:
            cursor = conn.cursor()
            cursor.execute(sql)

            # If it's not a SELECT (e.g., UPDATE/INSERT)
            if cursor.description is None:
                conn.commit()
                return True, []

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

            # Pretty print table
            table = Table(title="Query Result")

            for col in columns:
                table.add_column(col)

            for row in rows:
                table.add_row(*[str(x) for x in row])

            console.print(table)

            return True, rows

        except Exception as e:
            return False, str(e)

    # =========================
    # Read schema from DB
    # =========================
    def read_schema(self, conn):
        cursor = conn.cursor()

        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}
        relations = []

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
            schema[table] = cols

        # Get foreign keys
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            for row in cursor.fetchall():
                relations.append({
                    "from_table": table,
                    "from_column": row[3],
                    "to_table": row[2],
                    "to_column": row[4]
                })

        return schema, relations