import sqlite3

from agents.nlu_agent import NLUAgent
from agents.sql_planner_agent import SQLPlannerAgent
from agents.execution_agent import ExecutionAgent

# 🔐 SAFETY LAYER
from core.sql_safety import validate_sql, SQLSafetyError


class Orchestrator:
    def __init__(self, db_path):
        self.load_database(db_path)

        self.nlu = NLUAgent()
        self.planner = SQLPlannerAgent()
        self.executor = ExecutionAgent()

    # =========================
    # LOAD DATABASE
    # =========================
    def load_database(self, db_path):
        try:
            if hasattr(self, "conn"):
                self.conn.close()
            self.conn = sqlite3.connect(db_path)
            self.current_db = db_path
            print(f"✅ Loaded database: {db_path}")
        except Exception as e:
            print(f"❌ Failed to load database: {e}")
            raise

    # =========================
    # MAIN ENTRY POINT
    # =========================
    def handle_query(self, user_input):

        # =========================
        # SHOW TABLES
        # =========================
        if user_input.strip().lower() == "show tables":
            tables = self.executor.show_tables(self.conn)
            return {
                "sql": None,
                "result": tables,
                "explanation": "Listed all tables in database.",
                "confidence": 1.0
            }

        # =========================
        # DESCRIBE TABLE
        # =========================
        if user_input.strip().lower().startswith("describe "):
            table_name = user_input.strip().split()[1]
            schema = self.executor.describe_table(self.conn, table_name)
            return {
                "sql": None,
                "result": schema,
                "explanation": f"Described table {table_name}.",
                "confidence": 1.0
            }

        # =========================
        # IMPORT CSV
        # =========================
        if user_input.strip().lower().startswith("import "):
            parts = user_input.strip().split()
            csv_path = parts[1]
            table_name = parts[3]

            self.executor.import_csv(self.conn, csv_path, table_name)
            return {
                "sql": None,
                "result": None,
                "explanation": f"Imported {csv_path} as {table_name}",
                "confidence": 1.0
            }

        # =========================
        # LOAD DATABASE
        # =========================
        if user_input.strip().lower().startswith("load "):
            new_db = user_input.strip()[5:].strip()
            self.load_database(new_db)
            return {
                "sql": None,
                "result": None,
                "explanation": f"Switched to database: {new_db}",
                "confidence": 1.0
            }

        # =========================
        # NORMAL PIPELINE
        # =========================
        try:
            schema, relations = self.executor.read_schema(self.conn)

            print("\n[1] Understanding question...")
            intent = self.nlu.parse(user_input, schema)

            print("\n[2] Reading database schema...")
            print("[Schema Detected]:", {"tables": schema, "relations": relations})
            print("[Intent Detected]:", intent)

            print("[3] Planning SQL...")
            sql = self.planner.generate_sql(intent, schema, relations, self.conn)

            # 🚨 HARD BLOCK: Planner failure
            if sql is None or "None" in str(sql):
                raise SQLSafetyError("Planner failed to produce valid SQL")

            # 🚨 HARD BLOCK: Only allow SELECT
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith("SELECT"):
                raise SQLSafetyError("Only SELECT queries are allowed")

            # =========================
            # 🔐 SAFETY VALIDATION
            # =========================
            validate_sql(sql, {"tables": schema})

            print("[4] Executing SQL...")
            result = self.executor.execute(sql, self.conn)

            return {
                "sql": sql,
                "result": result,
                "explanation": "Query executed successfully.",
                "confidence": 1.0
            }

        # =========================
        # SAFETY BLOCK
        # =========================
        except SQLSafetyError as e:
            print("🛑 SAFETY BLOCKED QUERY:", e)

            return {
                "sql": None,
                "result": None,
                "explanation": f"Query rejected by safety layer: {e}",
                "confidence": 0.0
            }

        # =========================
        # SYSTEM FAILURE
        # =========================
        except Exception as e:
            print("❌ SYSTEM ERROR:", e)

            return {
                "sql": None,
                "result": None,
                "explanation": f"System error: {e}",
                "confidence": 0.0
            }