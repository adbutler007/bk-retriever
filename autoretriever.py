from data_loader import DataLoader
from llama_index.node_parser import (
    HierarchicalNodeParser, )
from llama_index.node_parser import get_leaf_nodes, get_root_nodes
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage import StorageContext
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.retrievers.auto_merging_retriever import AutoMergingRetriever
from llama_index.llms import OpenAI
from llama_index import Document as LlamaDocument
from llama_index.schema import Document as Document


class QueryRetriever:

  def __init__(self, index_path, model="gpt-4-1106-preview"):
    self.loader = DataLoader(index_path)
    documents = self.loader.load_and_process_data()

    doc_text = ' '.join(
        [doc.text for stem in documents for doc in documents[stem]])
    docs = [LlamaDocument(text=doc_text)]

    node_parser = HierarchicalNodeParser.from_defaults()
    nodes = node_parser.get_nodes_from_documents(docs)

    leaf_nodes = get_leaf_nodes(nodes)
    root_nodes = get_root_nodes(nodes)

    # define storage context
    docstore = SimpleDocumentStore()

    # insert nodes into docstore
    docstore.add_documents(nodes)

    # define storage context (will include vector store by default too)
    storage_context = StorageContext.from_defaults(docstore=docstore)

    service_context = ServiceContext.from_defaults(llm=OpenAI(model=model))

    base_index = VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
        service_context=service_context,
    )

    base_retriever = base_index.as_retriever(similarity_top_k=6)
    self.retriever = AutoMergingRetriever(base_retriever,
                                          storage_context,
                                          verbose=True)

  def get_retriever(self):
    return self.retriever
