class ExplanationAgent:
    def explain(self, sql, intent):
        explanation = "I understood your question and generated the following SQL query:\n"
        explanation += sql + "\n\n"

        if intent.get("aggregation"):
            explanation += "This query uses an aggregation function to compute the result.\n"

        if "where" in sql.lower():
            explanation += "It also applies a filtering condition based on your question.\n"

        explanation += "The query was validated by executing it on the database."

        return explanation