from retrieve import retrieve_tables
from expand import expand_with_fks
from classify import classify_query, OUT_OF_SCOPE_MESSAGE, GENERAL_RESPONSE_MESSAGE
from generate import generate_sql
import sqlglot
from sqlglot import exp
from validate import validate_is_select, validate_tables_exist, validate_columns_exist

#handle query after triage
def handle_query(question: str, model, conn, all_tables: list) -> dict:
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

    return {"status": "ok", "type": "data_question", "sql": sql}
    # execution (Step 7) plugs in right here, once built — run `sql`, attach results


def build_schema_context(question: str, model, conn, all_tables: list, k: int = 3) -> str:
    retrieved = retrieve_tables(question, model, conn, k=k)
    retrieved_names = [r[0] for r in retrieved]

    expanded_names = expand_with_fks(retrieved_names, all_tables)

    # read stored descriptions directly from table_embeddings — same text that was embedded,
    # not regenerated — keeps retrieval and generation context guaranteed consistent
    cur = conn.cursor()
    cur.execute(
        "SELECT table_name, description FROM table_embeddings WHERE table_name = ANY(%s)",
        (list(expanded_names),)
    )
    rows = cur.fetchall()
    cur.close()

    descriptions = [row[1] for row in rows]
    return "\n\n".join(descriptions)