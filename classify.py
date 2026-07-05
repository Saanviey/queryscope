import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

OUT_OF_SCOPE_MESSAGE = "I can only answer questions based on the connected database's schema. Try asking something related to the data available."
GENERAL_RESPONSE_MESSAGE = "I turn natural language questions into SQL queries against a connected database and return the results. Ask me things like 'show me all high priority tickets' or 'which customers spent the most last month' — I'll figure out the right tables and write the query for you."

def classify_query(question: str) -> str:
    prompt = f"""Classify the user's question into exactly one category. Respond with ONLY the category label, nothing else.

Categories:
- data_question: anything that could be answered by querying the connected database — specific lookups, aggregates, filters, or comparisons over its records.
- general_question: questions about this system itself — what it does, what kind of data it has access to, how to use it.
- out_of_scope: anything unrelated to this system or its data — general knowledge, chit-chat, unrelated topics.

If in doubt between data_question and either other category, choose data_question.

Question: {question}

Category:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()