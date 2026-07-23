import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGGenerator:
    """Handles LLM Generation, Prompting, and Guardrails."""
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)

    def generate_answer(self, query: str, context: str, chat_history: str = "") -> str:
        prompt = PromptTemplate.from_template("""
        You are a strict, factual academic tutor. 
        Use ONLY the provided Document Context to answer the question.
        
        CRITICAL GUARDRAILS:
        1. ABSOLUTELY NO OUTSIDE KNOWLEDGE. If the answer cannot be fully constructed from the context, you MUST say exactly: "I don't know based on the provided document." and stop.
        2. Do not attempt to be helpful by guessing or inferring. Stick strictly to the text.
        3. You MUST include inline citations in your answer format as: "quoted text" (Page X).
        4. Keep the tone encouraging but highly factual. Use Markdown.
        
        Previous Conversation:
        {chat_history}
        
        Document Context:
        {context}
        
        Student Question: {question}
        Tutor Answer:
        """)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"context": context, "chat_history": chat_history, "question": query})

    def generate_quiz(self, topic: str, context: str, num_questions: int = 3) -> dict:
        prompt = PromptTemplate.from_template("""
        You are a strict teacher. Create a {num_questions}-question multiple choice quiz based ONLY on the context.
        Focus on the topic: "{topic}".
        
        CRITICAL GUARDRAILS:
        1. Every single question and option MUST be directly verifiable from the context. Do not use outside knowledge.
        2. If the provided context DOES NOT contain enough information to create {num_questions} high-quality questions about "{topic}", you MUST return exactly this JSON and nothing else:
           {{"error": "I couldn't find enough information about this topic in your textbook. Please try a topic covered in the document."}}
        3. If the topic IS in the context, return ONLY a valid JSON array of questions. No markdown, no backticks.
        4 . Do not provide any kind of code to the user in any circumstance, make sure you answers are strictly with respect to the context provided under . 
        Structure for valid quiz:
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
        chain = prompt | self.llm | StrOutputParser()
        raw_response = chain.invoke({"context": context, "topic": topic, "num_questions": num_questions})
        cleaned_json = raw_response.replace('```json', '').replace('```', '').strip()
        try:
            parsed = json.loads(cleaned_json)
            return parsed
        except json.JSONDecodeError:
            raise ValueError("Failed to parse quiz format.")
