import json
import re
from chatgpt_engine import generate_sql, select_table_dynamically
from sql_validator import validate_sql
from db import execute_sql

# ---------------------------------
# 1. LOAD STRUCTURE
# ---------------------------------
with open("structure3.json", encoding="utf-8") as f:
    STRUCTURE = json.load(f)

def clean_llm_sql(sql: str) -> str:
    """Removes markdown blocks and extra characters."""
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.replace(";", "")
    return sql.strip()

def run_chatbot():
    print("\n===== AUTOPLANT METADATA-DRIVEN CHATBOT =====")
    
    while True:
        try:
            question = input("\nAsk a question (or 'exit'): ").strip()
            if not question: continue
            if question.lower() in ['exit', 'quit']: break

            # -------------------------------------------------
            # 2. DYNAMIC TABLE SELECTION
            # -------------------------------------------------
            # The AI looks at Description, Authoritative For, and Terms
            locked_table = select_table_dynamically(question, STRUCTURE)
            
            if locked_table == "UNKNOWN" or locked_table not in STRUCTURE["tables"]:
                print(f"❌ Table Selection Error: No matching table found for your request.")
                continue

            print(f"🔐 Selected Table: {locked_table}")
            table_definition = STRUCTURE["tables"][locked_table]

            # -------------------------------------------------
            # 3. SQL GENERATION (Metadata-Driven)
            # -------------------------------------------------
            raw_sql = generate_sql(question, locked_table, table_definition)

            if raw_sql == "UNSUPPORTED_QUERY":
                print("❌ Unsupported query: The metadata does not support this request.")
                continue

            # -------------------------------------------------
            # 4. CLEAN & VALIDATE
            # -------------------------------------------------
            sql = clean_llm_sql(raw_sql)
            
            # The validator now uses the columns from the auto-selected table
            validate_sql(sql, STRUCTURE)

            print(f"🧪 FINAL SQL:\n{sql}")

            # -------------------------------------------------
            # 5. EXECUTE
            # -------------------------------------------------
            results = execute_sql(sql)

            print("\n✅ RESULT:")
            if not results:
                print("No records found.")
            else:
                print(results)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ ERROR: {e}")

if __name__ == "__main__":
    run_chatbot()