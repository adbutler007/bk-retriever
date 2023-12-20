from llama_index import SimpleDirectoryReader, SummaryIndex, ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
from llama_index.node_parser.text.sentence import SentenceSplitter
from pathlib import Path
from typing import Dict, Any
import os

class DataLoader:
    def __init__(self, index_path):
        self.index_path = index_path
        self.llm = OpenAI(temperature=0, model="gpt-4-1106-preview")
        self.embed_model = OpenAIEmbedding
        self.service_context = ServiceContext.from_defaults(llm=self.llm, embed_model=self.embed_model)

    def load_data(self):
        """
        Load all documents
        """
        if not os.path.exists(self.index_path):
            print(f"No directory found at {self.index_path}. Please ensure the directory exists.")
            return None

        try:
            documents = {}
            filenames = os.listdir(self.index_path)
            for filename in filenames:
                stem = Path(filename).stem
                reader = SimpleDirectoryReader(input_files=[os.path.join(self.index_path, filename)])
                documents[stem] = reader.load_data()

            print(f"Documents loaded from {self.index_path}")
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return None

    def get_doc_descriptions(self, documents):
        """Get document descriptions."""
        node_parser = SentenceSplitter()
        responses = {}
        for stem, doc in documents.items():
            nodes = node_parser.get_nodes_from_documents(doc)
            # build summary index
            summary_index = SummaryIndex(nodes, service_context=self.service_context)
            # define query engines
            summary_query_engine = summary_index.as_query_engine()
            query = """The document itself will be used as a tool in a context retrieval pipeline. Provide a 60 character dense description describing when this tool might be useful. Always include the most important, unique or special terms mentioned in the document or title in order of importance. Be as concise and information dense as possible and never more than 65 characters, lower case with no punctuation.
            Example:
            return stacking leverage tracking error efficient
            """
            response = summary_query_engine.query(query)
            responses[stem] = str(response)
            print(f'==={len(str(response))}===')
        return responses

    def load_and_process_data(self):
        documents = self.load_data()
        doc_descriptions = {}
        if documents is not None:
            doc_descriptions = self.get_doc_descriptions(documents)
            for stem in documents:
                if stem in doc_descriptions:
                    for doc in documents[stem]:
                        doc.metadata['file_name'] = doc_descriptions[stem]
        return documents, doc_descriptions
    
#documents = load_data(index_path)