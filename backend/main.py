import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
from ingest import ingest_schema
from sentence_transformers import SentenceTransformer
import psycopg2
from pipeline_router import handle_query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# loaded once at startup, reused across every request
DATABASE_URL = "postgresql://manoj@localhost/chinook"
READONLY_URL = "postgresql://queryscope_readonly:changeme@localhost/chinook"

model = SentenceTransformer('all-MiniLM-L6-v2')
tables = ingest_schema(DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL)

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def query(request: QueryRequest):
    return handle_query(request.question, model, conn, tables, READONLY_URL)

INFRA_TABLES = {"table_embeddings"}
tables = [t for t in ingest_schema(DATABASE_URL) if t.name not in INFRA_TABLES]

@app.get("/schema")
def get_schema():
    return [
        {
            "name": t.name,
            "columns": [
                {"name": c.name, "type": c.type, "is_primary_key": c.is_primary_key}
                for c in t.columns
            ],
            "foreign_keys": [
                {"column": fk.column, "ref_table": fk.ref_table, "ref_column": fk.ref_column}
                for fk in t.foreign_keys
            ],
        }
        for t in tables
    ]