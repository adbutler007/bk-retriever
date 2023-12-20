from fastapi import FastAPI
from autoretriever import QueryRetriever

app = FastAPI()

index_path = "./data"
retriever_obj = QueryRetriever(index_path)
retriever = retriever_obj.get_retriever()

@app.get("/retrieve/")
async def retrieve(query: str):
    nodes = retriever.retrieve(query)
    full_context = '\n\n'.join([node.text for node in nodes])
    return {"full_context": full_context}