"""Customer support chatbot PoC.

Answers policyholder questions using their contract data as context.
"""

import os
import sqlite3

from fastapi import FastAPI
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
app = FastAPI()

SYSTEM_PROMPT = (
    "You are a helpful support assistant for Acme Insurance. "
    "Answer questions about the customer's policy using the provided "
    "customer record. Be concise and friendly."
)


def load_customer(customer_id: int) -> dict:
    conn = sqlite3.connect("customers.db")
    row = conn.execute(
        "SELECT full_name, email, birth_date, address, policy_number, "
        "policy_type, monthly_premium FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()
    conn.close()
    return {
        "full_name": row[0],
        "email": row[1],
        "birth_date": row[2],
        "address": row[3],
        "policy_number": row[4],
        "policy_type": row[5],
        "monthly_premium": row[6],
    }


@app.post("/chat/{customer_id}")
def chat(customer_id: int, question: str):
    customer = load_customer(customer_id)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Customer record: {customer}\n\nQuestion: {question}",
            },
        ],
    )
    return {"answer": response.choices[0].message.content}
