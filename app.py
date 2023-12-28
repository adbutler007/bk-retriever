from fastapi import FastAPI, Depends
from autoretriever import QueryRetriever
from typing import Callable

app = FastAPI()

# Global variable to store the retriever instance so it's only created once
retriever_instance = None


def get_retriever():
  global retriever_instance
  if retriever_instance is None:  # Only create the retriever if it doesn't exist
    index_path = "./data"
    retriever_obj = QueryRetriever(index_path)
    retriever_instance = retriever_obj.get_retriever()
  return retriever_instance


@app.get("/retrieve/")
async def retrieve(query: str, retriever: Callable = Depends(get_retriever)):
  # Append the query to the text file
  with open("./tmp/queries.txt", "a") as file:
    file.write(query + "\n")

  nodes = retriever.retrieve(query)
  full_context = '\n\n'.join([node.text for node in nodes])
  return {"full_context": full_context}
