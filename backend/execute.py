import psycopg2

#executes the generated and verified sql by llm
def execute_sql(sql: str, readonly_url: str) -> list[dict]:
    conn = psycopg2.connect(readonly_url)
    cur = conn.cursor()
    cur.execute(sql)

    columns = [desc[0] for desc in cur.description]  # column names from the result
    rows = cur.fetchall()

    results = [dict(zip(columns, row)) for row in rows]  # convert each row into {column: value}

    cur.close()
    conn.close()
    return results