import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_purpose(table) -> str:
    col_names = ", ".join(c.name for c in table.columns)
    fk_text = ", ".join(f"{fk.column} -> {fk.ref_table}" for fk in table.foreign_keys) or "none"

    prompt = f"""Write one concise sentence describing the purpose of a database table, based on its structure. No preamble, just the sentence.

    Table name: {table.name}
    Columns: {col_names}
    Foreign keys: {fk_text}

    Sentence:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def generate_description(table) -> str:
    col_text = ", ".join(f"{c.name} ({c.type})" for c in table.columns)

    if table.foreign_keys:
        fk_text = ", ".join(
            f"{fk.column} -> {fk.ref_table}.{fk.ref_column}" for fk in table.foreign_keys
        )
    else:
        fk_text = "none"

    purpose = generate_purpose(table)  # was: f"Stores records related to {table.name}."

    return (
        f"Table: {table.name}\n"
        f"Columns: {col_text}\n"
        f"Foreign keys: {fk_text}\n"
        f"Purpose: {purpose}"
    )