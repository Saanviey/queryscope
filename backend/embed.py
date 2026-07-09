import psycopg2
from ingest import ingest_schema
from describe import generate_description
from sentence_transformers import SentenceTransformer

#embed schema description to vector db, inbuilt pgvector in postgres 

INFRA_TABLES = {"table_embeddings"}  # tables that are pipeline infrastructure, not schema domain data

def embed_and_store(database_url_sqlalchemy: str, database_url_psycopg2: str):
    tables = ingest_schema(database_url_sqlalchemy)
    tables = [t for t in tables if t.name not in INFRA_TABLES]  # exclude infra tables

    model = SentenceTransformer('all-MiniLM-L6-v2')
    conn = psycopg2.connect(database_url_psycopg2)
    cur = conn.cursor()

    for table in tables:
        desc = generate_description(table)
        vector = model.encode(desc).tolist()
        vector_str = "[" + ",".join(str(x) for x in vector) + "]"

        cur.execute(
            """
            INSERT INTO table_embeddings (table_name, description, embedding)
            VALUES (%s, %s, %s)
            ON CONFLICT (table_name) DO UPDATE
            SET description = EXCLUDED.description, embedding = EXCLUDED.embedding
            """,
            (table.name, desc, vector_str)
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Stored embeddings for {len(tables)} tables.")