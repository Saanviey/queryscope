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
    #retry logic if an attempt fails
    max_attempts = 3
    sql = None
    last_error = None

    for attempt in range(max_attempts):
        sql = generate_sql(question, model, conn, all_tables, previous_error=last_error)

        try:
            parsed = sqlglot.parse_one(sql)
        except Exception as e:
            last_error = f"SQL failed to parse: {e}"
            continue

        if not validate_is_select(parsed):
            last_error = "Only SELECT statements are allowed"
            continue

        missing_tables = validate_tables_exist(parsed, all_tables)
        if missing_tables:
            last_error = f"Unknown table(s): {missing_tables}"
            continue

        missing_columns = validate_columns_exist(parsed, all_tables)
        if missing_columns:
            last_error = f"Unknown/ambiguous column(s): {missing_columns}"
            continue

        last_error = None
        break

    if last_error:
        return {"status": "rejected", "reason": last_error}
    
    
    #execute final sql after max_attempts
    try:
        results = execute_sql(sql, readonly_url )
    except Exception as e:
        return {"status": "error", "reason": str(e)}
    #return result along with the number of attempts so far
    return {"status": "ok", "type": "data_question", "sql": sql, "results": results, "attempts": attempt + 1}