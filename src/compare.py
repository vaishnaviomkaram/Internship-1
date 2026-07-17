from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class DocumentComparator:
    """Handles the Mini-Extension: Multi-document reasoning and comparison."""
    def __init__(self, llm):
        self.llm = llm

    def compare(self, query: str, context_doc1: str, doc1_name: str, context_doc2: str, doc2_name: str) -> str:
        prompt = PromptTemplate.from_template("""
        You are an expert academic analyst. Compare the two provided documents based ONLY on the student's query and the provided contexts.
        
        CRITICAL GUARDRAILS:
        1. ZERO HALLUCINATION: Only discuss concepts that are explicitly present in Context 1 or Context 2. 
        2. If the query asks about a topic not found in either context, state exactly: "Neither document mentions this topic." and stop.
        3. Use inline citations: "text" (Doc 1, Page X) or "text" (Doc 2, Page Y).
        4. Maintain a helpful, beginner-friendly tone.
        5. Do not provide Any Kind of Code to the User or anything extra apart from the docs , if the user asks for a query make sure to provide in a comparisional context but do not every provide any code or anything else apart from the document context
        
        Document 1 ({doc1_name}) Context:
        {context1}
        
        Document 2 ({doc2_name}) Context:
        {context2}
        
        Student Query: {query}
        
        Comparative Analysis:
        """)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "context1": context_doc1, 
            "doc1_name": doc1_name,
            "context2": context_doc2, 
            "doc2_name": doc2_name,
            "query": query
        })