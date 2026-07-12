import os
from groq import Groq
from pipeline import build_schema_context

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

#updated to accept optional error info for futher retry attempts
def generate_sql(question: str, model, conn, all_tables: list, previous_error: str = None) -> str:
    schema_context = build_schema_context(question, model, conn, all_tables)

    retry_note = ""
    if previous_error:
        retry_note = f"\n\nYour previous attempt failed validation with this error: {previous_error}\nFix the query to address this specific issue."

    prompt = f"""You are a SQL generator. Given the schema below and a question, output ONLY a single SELECT statement. No prose, no markdown fences, no explanation.

Always qualify column names with their table name or alias when the query involves more than one table.

Schema:
{schema_context}

Question: {question}{retry_note}

SQL:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()













