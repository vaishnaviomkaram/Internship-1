import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.retrievers import EnsembleRetriever      # <-- Fixed!
from langchain_community.retrievers import BM25Retriever



class RAGPipeline:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        # Swapped to Gemini 1.5 Flash: 100% free tier, extremely fast, great at following strict instructions
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0)
        
    def _setup_hybrid_retriever(self, search_kwargs={"k": 3}):
        """Combines Chroma (semantic) and BM25 (keyword) for better accuracy."""
        # 1. Dense Retriever (Chroma)
        dense_retriever = self.vector_store.as_retriever(search_kwargs=search_kwargs)
        
        # 2. Sparse Retriever (BM25)
        all_docs = self.vector_store.get()
        from langchain_core.documents import Document
        docs = [Document(page_content=text, metadata=meta) for text, meta in zip(all_docs['documents'], all_docs['metadatas'])]
        
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = search_kwargs["k"]
        
        # 3. Ensemble (50% weight to each)
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, dense_retriever], weights=[0.5, 0.5]
        )
        return hybrid_retriever

    def generate_answer(self, query: str):
        retriever = self._setup_hybrid_retriever()
        
        # Retrieve relevant chunks
        retrieved_docs = retriever.invoke(query)
        
        # Format context for Gemini
        context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in retrieved_docs])
        
        # Strict Prompt adhering to Guardrails and Citations
        prompt = PromptTemplate.from_template("""
        You are an expert academic assistant. Use ONLY the provided context to answer the question.
        
        CRITICAL RULES:
        1. If the answer is not contained in the context, you MUST say exactly: "I don't know based on the provided document." Do not guess.
        2. You MUST include inline citations in your answer format as: "quoted text" (Page X).
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """)

        # Build the LangChain pipeline
        chain = (
            prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        answer = chain.invoke({"context": context, "question": query})
        return answer, retrieved_docs