from classify import classify_query, OUT_OF_SCOPE_MESSAGE, GENERAL_RESPONSE_MESSAGE
from generate import generate_sql
from execute import execute_sql
import sqlglot
from sqlglot import exp
from validate import validate_is_select, validate_tables_exist, validate_columns_exist

def handle_query(question: str, model, conn, all_tables: list, readonly_url: str) -> dict:
    category = classify_query(question)

    if category == "out_of_scope":
        return {"status": "ok", "type": "out_of_scope", "message": OUT_OF_SCOPE_MESSAGE}

    if category == "general_question":
        return {"status": "ok", "type": "general_question", "message": GENERAL_RESPONSE_MESSAGE}

    # category == "data_question" from here on
    sql = generate_sql(question, model, conn, all_tables)

    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as e:
        return {"status": "rejected", "reason": f"SQL failed to parse: {e}"}

    if not validate_is_select(parsed):
        return {"status": "rejected", "reason": "Only SELECT statements are allowed"}

    missing_tables = validate_tables_exist(parsed, all_tables)
    if missing_tables:
        return {"status": "rejected", "reason": f"Unknown table(s): {missing_tables}"}

    missing_columns = validate_columns_exist(parsed, all_tables)
    if missing_columns:
        return {"status": "rejected", "reason": f"Unknown/ambiguous column(s): {missing_columns}"}

    try:
        results = execute_sql(sql, readonly_url)
    except Exception as e:
        return {"status": "error", "reason": str(e)}

    return {"status": "ok", "type": "data_question", "sql": sql, "results": results}