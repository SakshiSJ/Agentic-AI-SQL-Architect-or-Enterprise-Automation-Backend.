# import json # <--- Add this import
# from openai import OpenAI

# client = OpenAI(api_key="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")

# def generate_sql(question: str, forced_table: str, table_definition: dict): # <--- Change this argument
    
#     # Convert the full JSON definition to a string so the LLM can see business_terms
#     table_json = json.dumps(table_definition, indent=2)

#     system_prompt = f"""
# You are an enterprise SQL generator.

# STRICT RULES:
# 1. Generate exactly ONE valid MySQL SELECT query.
# 2. Use ONLY this table: `{forced_table}`.
# 3. Use the JSON below to map user terms (like 'yard' or 'PPC') to real columns/values using 'business_terms'.
# 4. If 'default_filters' exist in the JSON, you MUST include them (e.g., `TRIP STATUS` = 'A').
# 5. Always wrap column names with backticks.
# 6. Return ONLY raw SQL. No markdown.

# TABLE DEFINITION:
# {table_json}

# If not possible, return exactly: UNSUPPORTED_QUERY
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": question}
#         ],
#         temperature=0
#     )
    
#     # Add a safety check for the NoneType error
#     content = response.choices[0].message.content
#     return content.strip() if content else "UNSUPPORTED_QUERY"import json
from openai import OpenAI
import json

# Initialize your client
client = OpenAI(api_key="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")

def select_table_dynamically(question, structure):
    """
    Looks at all tables in the JSON and picks the right one based on 
    Description, Authoritative_for, and Business_terms.
    """
    # Create a simplified 'menu' of all tables for the LLM to scan
    table_options = {}
    for name, meta in structure["tables"].items():
        table_options[name] = {
            "description": meta.get("description"),
            "authoritative_for": meta.get("authoritative_for", []),
            "terms_it_understands": list(meta.get("business_terms", {}).keys())
        }

    prompt = f"""
Act as a Database Router for AutoPlant. Given the user question and the table metadata below, 
identify which Table ID is the most authoritative source to answer the question.

USER QUESTION: "{question}"

AVAILABLE TABLES AND THEIR SCOPE:
{json.dumps(table_options, indent=2)}

STRICT RULES:
1. Return ONLY the table ID string (e.g., "vw_active_trip" or "tbl_ap_hist_rep_ob").
2. Do not explain your choice.
3. If no table matches at all, return "UNKNOWN".
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return response.choices[0].message.content.strip().replace("`", "")

def generate_sql(question, table_name, table_definition):
    """
    Generates SQL using the full metadata block for that specific table.
    """
    from sql_prompt import get_system_prompt
    
    # We use a single strong prompt now instead of separating phases
    system_prompt = get_system_prompt(table_name, table_definition)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content.strip()