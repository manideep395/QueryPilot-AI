# core/sql_safety.py

import re

class SQLSafetyError(Exception):
    pass

def extract_tables(sql):
    # Very simple extractor (enough for your project)
    tokens = re.split(r"\s+", sql.upper())
    tables = []

    for i, tok in enumerate(tokens):
        if tok in ["FROM", "JOIN"] and i + 1 < len(tokens):
            t = tokens[i + 1].replace(",", "").strip()
            tables.append(t)

    return tables

def extract_columns(sql):
    # Only checks SELECT part
    sql = sql.upper()
    if "SELECT" not in sql or "FROM" not in sql:
        return []

    select_part = sql.split("FROM")[0].replace("SELECT", "")
    cols = []

    for c in select_part.split(","):
        c = c.strip()
        if "(" in c:  # COUNT(x)
            inside = c[c.find("(")+1:c.find(")")]
            cols.append(inside.strip())
        else:
            if "." in c:
                c = c.split(".")[1]
            cols.append(c.strip())

    return cols

def validate_sql(sql, schema):
    if sql is None:
        raise SQLSafetyError("SQL is None")

    sql_upper = sql.upper()

    # 1. Block multi-statement / injection
    if ";" in sql_upper:
        raise SQLSafetyError("Multiple statements blocked")

    # 2. Block FROM None
    if "FROM NONE" in sql_upper:
        raise SQLSafetyError("Table resolution failed")

    # 3. Check tables
    schema_tables = set(schema["tables"].keys())

    used_tables = extract_tables(sql_upper)

    for t in used_tables:
        if t not in schema_tables:
            raise SQLSafetyError(f"Illegal table used: {t}")

    # 4. Check columns
    schema_columns = set()
    for t, cols in schema["tables"].items():
        for c in cols:
            schema_columns.add(c.upper())

    used_columns = extract_columns(sql_upper)

    for c in used_columns:
        if c == "*" or c == "":
            continue
        if c.upper() not in schema_columns:
            raise SQLSafetyError(f"Illegal column used: {c}")

    # 5. Basic sanity
    if "SELECT" not in sql_upper or "FROM" not in sql_upper:
        raise SQLSafetyError("Not a valid SELECT query")

    return True