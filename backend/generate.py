import os
from groq import Groq
from pipeline import build_schema_context

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_sql(question: str, model, conn, all_tables: list) -> str:
    schema_context = build_schema_context(question, model, conn, all_tables)

    prompt = f"""You are a SQL generator. Given the schema below and a question, output ONLY a single SELECT statement. No prose, no markdown fences, no explanation.

Schema:
{schema_context}

Question: {question}

SQL:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content