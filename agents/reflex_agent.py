class ReflexAgent:
    def fix(self, sql, error):
        print("ReflexAgent analyzing error...")

        if "no such column" in error.lower():
            if "score" in sql:
                print("Fixing: score -> marks")
                return sql.replace("score", "marks")

        return sql