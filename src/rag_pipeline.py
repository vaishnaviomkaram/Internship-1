import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

class RAGPipeline:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        # Using Gemini 1.5 Flash: fast and great at JSON instruction following
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)  #gemma-4-26b-a4b-it
        
    def _setup_hybrid_retriever(self, search_kwargs={"k": 3}):
        """Combines Chroma (semantic) and BM25 (keyword) for better accuracy."""
        dense_retriever = self.vector_store.as_retriever(search_kwargs=search_kwargs)
        
        all_docs = self.vector_store.get()
        from langchain_core.documents import Document
        docs = [Document(page_content=text, metadata=meta) for text, meta in zip(all_docs['documents'], all_docs['metadatas'])]
        
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = search_kwargs["k"]
        
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, dense_retriever], weights=[0.5, 0.5]
        )
        return hybrid_retriever

    def generate_answer(self, query: str, chat_history: str = ""):
        """Generates an answer using hybrid search and conversation memory."""
        retriever = self._setup_hybrid_retriever()
        retrieved_docs = retriever.invoke(query)
        context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in retrieved_docs])
        
        # Updated prompt to include conversation history
        prompt = PromptTemplate.from_template("""
        You are an expert academic assistant. Use ONLY the provided Document Context to answer the question.
        
        CRITICAL RULES:
        1. If the answer is not contained in the context, you MUST say exactly: "I don't know based on the provided document." Do not guess.
        2. You MUST include inline citations in your answer format as: "quoted text" (Page X).
        
        Previous Conversation Context:
        {chat_history}
        
        Document Context:
        {context}
        
        Current Question: {question}
        
        Answer:
        """)

        chain = (prompt | self.llm | StrOutputParser())
        answer = chain.invoke({"context": context, "chat_history": chat_history, "question": query})
        return answer, retrieved_docs

    def generate_quiz(self, topic: str, num_questions: int = 3):
        """Fetches context and generates a JSON-structured quiz to preserve UI tokens."""
        # Widen search slightly to get better quiz context
        retriever = self._setup_hybrid_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.invoke(topic)
        context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in retrieved_docs])

        prompt = PromptTemplate.from_template("""
        You are a strict teacher. Create a {num_questions}-question multiple choice quiz based ONLY on the following context.
        Focus on the topic: "{topic}".

        CRITICAL INSTRUCTION: Return ONLY a valid JSON array. Do not include markdown blocks, backticks, or introduction text.
        Structure:
        [
            {{
                "question": "The question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The exact string of the correct option",
                "explanation": "Brief explanation with page citation"
            }}
        ]

        Context:
        {context}
        """)

        chain = (prompt | self.llm | StrOutputParser())
        raw_response = chain.invoke({"context": context, "topic": topic, "num_questions": num_questions})
        
        # Clean up JSON in case the LLM stubbornly returns markdown wrappers
        cleaned_json = raw_response.replace('```json', '').replace('```', '').strip()
        
        try:
            quiz_data = json.loads(cleaned_json)
            return quiz_data, retrieved_docs
        except json.JSONDecodeError:
            raise ValueError("Failed to parse quiz format. Please try again.")