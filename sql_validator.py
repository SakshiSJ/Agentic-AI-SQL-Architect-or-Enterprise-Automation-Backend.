import re


def clean_identifier(col: str) -> str:
    """
    Removes backticks and trims spaces.
    """
    return col.replace("`", "").strip()


# In sql_validator.py, find the part checking for SELECT *
# Inside sql_validator.py
import re

def validate_sql(sql: str, structure: dict):
    # 1. Identify the table name
    table_match = re.search(r"FROM\s+[`]?([\w]+)[`]?", sql, re.IGNORECASE)
    if not table_match:
        raise Exception("Could not find a valid table name in the SQL.")
    
    table_name = table_match.group(1).strip()
    if table_name not in structure["tables"]:
        raise Exception(f"Table '{table_name}' is not in metadata.")

    # 2. Get allowed columns (UPPERCASE)
    allowed_columns = [col.upper() for col in structure["tables"][table_name]["columns"].keys()]

    # 3. FIX: Improved Regex to extract ONLY what is inside backticks
    # This specifically avoids grabbing newlines or surrounding SQL keywords
    used_identifiers = re.findall(r"`([^`]+)`", sql)

    for item in used_identifiers:
        # Clean the extracted string (remove any accidental newlines)
        clean_item = item.strip()

        # Skip if it's the table name or an alias (aliases usually have spaces or aren't in metadata)
        if clean_item.lower() == table_name.lower():
            continue
        
        # If it's a real column, it MUST be in the allowed list
        # Note: We check if it's in the allowed list; if it's an alias like "Total Qty", 
        # we check the SQL to see if 'AS' comes before it.
        is_alias = re.search(rf"AS\s+[`]{re.escape(clean_item)}[`]", sql, re.IGNORECASE)
        
        if not is_alias and clean_item.upper() not in allowed_columns:
            raise Exception(f"Column '{clean_item}' is not allowed in table '{table_name}'.")

    return True
    # ... after extracting columns from the SQL ...
    if used_col.upper() not in allowed_cols:
        raise Exception(f"Column {used_col} is not allowed.")

    forbidden = [" JOIN ", " INNER ", " LEFT ", " RIGHT ", " UNION ", " WITH "]
    for kw in forbidden:
        if kw in sql_upper:
            raise Exception("JOIN / UNION / CTE not allowed")

    # ------------------------------------------------
    # 2️⃣ Extract Table
    # ------------------------------------------------
    table_match = re.search(r"\bFROM\s+([^\s;]+)", sql_upper)
    if not table_match:
        raise Exception("No table found")

    table = clean_identifier(table_match.group(1)).lower()

    if table not in structure["tables"]:
        raise Exception(f"Table not allowed: {table}")

    allowed_columns = set(
        structure["tables"][table]["columns"].keys()
    )

    # ------------------------------------------------
    # 3️⃣ SELECT Validation
    # ------------------------------------------------
    select_match = re.search(
        r"SELECT\s+(.*?)\s+FROM",
        sql,
        re.IGNORECASE | re.DOTALL
    )

    if not select_match:
        raise Exception("Invalid SELECT")

    select_part = select_match.group(1)

    if "*" in select_part:
        raise Exception("SELECT * is not allowed")

    select_cols = re.split(r",(?![^()]*\))", select_part)

    for col in select_cols:
        col = re.split(r"\s+AS\s+", col.strip(), flags=re.IGNORECASE)[0]
        col_clean = clean_identifier(col).upper()

        # Aggregation
        agg = re.match(r"(COUNT|SUM|AVG|MIN|MAX)\((.*?)\)", col_clean)
        if agg:
            inner = clean_identifier(agg.group(2)).upper()
            if inner.startswith("DISTINCT "):
                inner = inner.split(None, 1)[1]

            if inner != "*" and inner not in allowed_columns:
                raise Exception(f"Column not allowed in aggregation: {inner}")
            continue

        # DATE(), YEARWEEK(), YEAR(), MONTH()
        if col_clean.startswith("DATE("):
            inner = clean_identifier(col_clean[5:-1]).upper()
        elif col_clean.startswith("YEARWEEK("):
            inner = clean_identifier(
                col_clean[col_clean.find("(")+1:col_clean.find(")")].split(",")[0]
            ).upper()
        elif col_clean.startswith("YEAR(") or col_clean.startswith("MONTH("):
            inner = clean_identifier(
                col_clean[col_clean.find("(")+1:col_clean.find(")")]
            ).upper()
        else:
            inner = col_clean

        if inner not in allowed_columns:
            raise Exception(f"Column not allowed in SELECT: {col}")

    # ------------------------------------------------
    # 4️⃣ WHERE Validation
    # ------------------------------------------------
    where_match = re.search(
        r"WHERE\s+(.*?)(GROUP BY|ORDER BY|$)",
        sql,
        re.IGNORECASE | re.DOTALL
    )

    if where_match:
        conditions = re.split(
            r"\s+AND\s+",
            where_match.group(1),
            flags=re.IGNORECASE
        )

        for cond in conditions:
            cond = cond.strip()

            null_match = re.match(
                r"(`?[\w\s]+`?)\s+IS\s+(NOT\s+)?NULL",
                cond,
                re.IGNORECASE
            )
            if null_match:
                col = clean_identifier(null_match.group(1)).upper()
                if col not in allowed_columns:
                    raise Exception(f"Column not allowed in WHERE: {col}")
                continue

            eq_match = re.match(
                r"(`?[\w\s]+`?)\s*=\s*'?([^']+)'?",
                cond
            )
            if eq_match:
                col = clean_identifier(eq_match.group(1)).upper()
                if col not in allowed_columns:
                    raise Exception(f"Column not allowed in WHERE: {col}")

    # ------------------------------------------------
    # 5️⃣ GROUP BY Validation
    # ------------------------------------------------
    group_match = re.search(
        r"GROUP\s+BY\s+(.*?)(ORDER\s+BY|$)",
        sql,
        re.IGNORECASE | re.DOTALL
    )

    if group_match:
        group_cols = re.split(
            r",(?![^()]*\))",
            group_match.group(1)
        )

        for gcol in group_cols:
            g = clean_identifier(gcol.strip()).upper()

            if g.startswith("DATE("):
                inner = clean_identifier(g[5:-1]).upper()
            elif g.startswith("YEARWEEK("):
                inner = clean_identifier(
                    g[g.find("(")+1:g.find(")")].split(",")[0]
                ).upper()
            elif g.startswith("YEAR(") or g.startswith("MONTH("):
                inner = clean_identifier(
                    g[g.find("(")+1:g.find(")")]
                ).upper()
            else:
                inner = g

            if inner not in allowed_columns:
                raise Exception(f"Column not allowed in GROUP BY: {gcol}")

    return True
