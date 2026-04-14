import re

def build_sql(llm_sql: str) -> str:
    if not llm_sql or not isinstance(llm_sql, str):
        raise Exception("Invalid SQL")

    sql = llm_sql.strip()

    # Remove markdown
    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "").strip()

    # Only SELECT
    if not sql.upper().startswith("SELECT"):
        raise Exception("Only SELECT allowed")

    # Single statement only
    if ";" in sql[:-1]:
        raise Exception("Multiple statements not allowed")

    return sql
