from langchain_community.retrievers import BM25Retriever
# Using the classic namespace since langchain-classic is in your requirements.txt
from langchain_classic.retrievers import EnsembleRetriever 
from langchain_core.documents import Document

class RetrievalEngine:
    """Handles Hybrid Retrieval (Dense Semantic + BM25 Keyword)."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def get_hybrid_retriever(self, k: int = 4):
        dense_retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        
        # Fetch all docs for BM25 initialization
        all_docs = self.vector_store.get()
        docs = [
            Document(page_content=text, metadata=meta) 
            for text, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]
        
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = k
        
        # Ensemble: 50% Keyword (BM25), 50% Semantic (Dense)
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, dense_retriever], 
            weights=[0.5, 0.5]
        )
        return hybrid_retriever