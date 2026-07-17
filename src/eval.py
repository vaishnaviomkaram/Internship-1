import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGEvaluator:
    """LLM-as-a-Judge evaluation for RAG correctness, citation precision, and completeness."""
    def __init__(self, llm):
        self.llm = llm

    def evaluate_response(self, question: str, generated_answer: str, context: str) -> dict:
        prompt = PromptTemplate.from_template("""
        You are an expert AI Evaluator. Grade the generated answer based STRICTLY on the provided context.
        
        Axes to grade (1 to 5 scale):
        1. Correctness: Is the factual information accurate based STRICTLY on the context? IF THE ANSWER CONTAINS ANY OUTSIDE KNOWLEDGE OR HALLUCINATIONS, THE SCORE MUST BE 1.
        2. Citation Precision: Are the page numbers and quotes accurate and correctly formatted?
        3. Completeness: Does it fully answer the user's question using only the context?
        
        Question: {question}
        Context: {context}
        Generated Answer: {answer}
        
        Return ONLY a JSON object with the following structure (no markdown backticks):
        {{
            "correctness_score": <int>,
            "citation_score": <int>,
            "completeness_score": <int>,
            "feedback": "<brief constructive feedback pointing out any hallucinations or missing context>"
        }}
        """)
        chain = prompt | self.llm | StrOutputParser()
        raw = chain.invoke({"question": question, "context": context, "answer": generated_answer})
        cleaned = raw.replace('```json', '').replace('```', '').strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"correctness_score": 0, "citation_score": 0, "completeness_score": 0, "feedback": "Evaluation parsing failed."}