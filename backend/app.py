from fastapi import FastAPI
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

app = FastAPI()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

def search_docs(query: str):
    results = search_client.search(query, top=3)
    docs = []
    for r in results:
        docs.append(r["content"])
    return "\n".join(docs)

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/ask")
def ask_ai(q: str):
    context = search_docs(q)

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "You are a helpful AI support agent. Use the provided context to answer."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{q}"}
        ]
    )
    return {"response": response.choices[0].message.content}