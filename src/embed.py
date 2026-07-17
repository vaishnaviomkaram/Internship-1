from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

class EmbeddingManager:
    """Manages open-source embeddings and Vector DB operations."""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        # BGE is highly efficient and runs locally without API costs
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    def create_vector_store(self, chunks: List[Dict[str, Any]]) -> Chroma:
        documents = [
            Document(page_content=c["text"], metadata=c["metadata"]) 
            for c in chunks
        ]
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vector_store

    def load_vector_store(self) -> Chroma:
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )