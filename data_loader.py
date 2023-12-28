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
    self.service_context = ServiceContext.from_defaults(
        llm=self.llm, embed_model=self.embed_model)

  def load_data(self):
    """
        Load all documents
        """
    if not os.path.exists(self.index_path):
      print(
          f"No directory found at {self.index_path}. Please ensure the directory exists."
      )
      return None

    try:
      documents = {}
      filenames = os.listdir(self.index_path)
      for filename in filenames:
        stem = Path(filename).stem
        reader = SimpleDirectoryReader(
            input_files=[os.path.join(self.index_path, filename)])
        documents[stem] = reader.load_data()

      print(f"Documents loaded from {self.index_path}")
      return documents
    except Exception as e:
      print(f"Error loading documents: {e}")
      return None

  def get_doc_descriptions(self, documents):
    """Get document descriptions."""
    #node_parser = SentenceSplitter()
    responses = {}
    for stem, doc in documents.items():
      llm = OpenAI(temperature=0, model="gpt-3.5-turbo-instruct")
      query = f"""
      You will act as a filename modifier. Given a filename stem your job is to return a modified file name stem as a simple string removing any hash-like long sequences of letters and numbers. Always retain any numbers and other parts of the filename that are not obviously associated with the long hash-like sequence. Also remove any non-alphanumeric characters. Finally, connect all remaining words and numbers in the modified stem with underscores if they are not already.

      Example 1:
      Original stem: Lt Sir Percival Hawkings 2b642fc12c5b48b88c9ea5fcb5bd4c91
      Complete Answer: Lt_Sir_Percival_Hawkings

      Example 2:
      Original stem: Episode 22 - Madness in Muscovar, part 2 f622f262d79940b19b4b25a910702fe9
      Complete Answer: Episode_22_Madness_in_Muscovar_part_2

      Never prepend any apostrophes, quotation marks, or ticks. Always ONLY return the modified file stem as a simple string.

      Original stem: {stem}
      Complete Answer: <Always ONLY return the modified file stem as a simple string>
      """
      print(f'==={str(stem)}===')
      response = llm.complete(query)
      print(f'==={str(response)}===')
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
    return documents


#documents = load_data(index_path)
