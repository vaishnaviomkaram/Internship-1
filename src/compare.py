from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class DocumentComparator:
    """Handles the Mini-Extension: Multi-document reasoning and comparison."""
    
    def __init__(self, llm):
        self.llm = llm

    def compare(self, query: str, context_doc1: str, doc1_name: str, context_doc2: str, doc2_name: str) -> str:
        prompt = PromptTemplate.from_template("""
        You are an expert academic analyst. Compare the two provided documents based on the student's query.
        
        CRITICAL RULES:
        1. Highlight similarities and differences clearly using Markdown.
        2. Use inline citations like: "text" (Doc 1, Page X) or "text" (Doc 2, Page Y).
        3. If a point is only in one document, explicitly state that the other document omits it.
        4. Maintain a helpful, beginner-friendly tone.
        
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
