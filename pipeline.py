from retrieve import retrieve_tables
from expand import expand_with_fks


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