import streamlit as st
import os
from dotenv import load_dotenv

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.rag_pipeline import RAGPipeline

# Load API keys
load_dotenv()

st.set_page_config(page_title="AskMyBook", page_icon="📚", layout="centered")
st.title("📚 AskMyBook")
st.markdown("Your personal AI study buddy. Upload a book to chat and generate practice quizzes.")

# Setup directories
os.makedirs("data", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# --- Initialize Session States ---
if "db_ready" not in st.session_state:
    st.session_state.db_ready = os.path.exists("vectorstore/chroma.sqlite3")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_window" not in st.session_state:
    st.session_state.memory_window = 4  # Default memory length
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_graded" not in st.session_state:
    st.session_state.quiz_graded = False

# --- Sidebar: Document Upload ---
with st.sidebar:
    st.header("1. Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    if st.button("Process Document") and uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Parsing and creating vector embeddings..."):
            processor = DocumentProcessor()
            pages = processor.load_pdf(file_path)
            chunks = processor.chunk_documents(pages)
            
            db_manager = VectorStoreManager()
            db_manager.create_vector_store(chunks)
            st.session_state.db_ready = True
            st.success("Document processed! Vector database updated.")

# --- Main Interface Tabs ---
tab1, tab2 = st.tabs(["💬 Chat & Q&A", "🧠 Practice Quizzes"])

# ==========================================
# TAB 1: Conversational Q&A with Memory
# ==========================================
with tab1:
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("Document Q&A")
    with col2:
        # Settings popover for adjusting context window
        with st.popover("⚙️ Memory Settings"):
            st.markdown("**Adjust Context Window**")
            st.session_state.memory_window = st.number_input(
                "Prior messages to remember:", 
                min_value=0, max_value=20, value=st.session_state.memory_window, step=1,
                help="Higher numbers give the AI better memory but consume more tokens."
            )
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat Input
    if query := st.chat_input("Ask a question about the document..."):
        if not st.session_state.db_ready:
            st.error("Please upload and process a document first.")
        else:
            # Add user message to state and UI
            st.session_state.messages.append({"role": "user", "content": query})
            st.chat_message("user").write(query)

            # Format chat history slice based on user settings
            start_index = max(0, len(st.session_state.messages) - 1 - (st.session_state.memory_window))
            recent_history = st.session_state.messages[start_index:-1]
            history_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in recent_history])

            with st.spinner("Searching document and generating answer..."):
                try:
                    db_manager = VectorStoreManager()
                    db = db_manager.load_vector_store()
                    pipeline = RAGPipeline(vector_store=db)
                    
                    answer, source_docs = pipeline.generate_answer(query, chat_history=history_str)
                    
                    # Add AI response to UI and state
                    st.chat_message("assistant").write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    with st.expander("View Source Passages"):
                        for i, doc in enumerate(source_docs):
                            st.markdown(f"**Page {doc.metadata.get('page', 'Unknown')}**:")
                            st.caption(doc.page_content)
                            st.divider()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# ==========================================
# TAB 2: On-Demand Quizzes (Local Eval)
# ==========================================
with tab2:
    st.subheader("On-Demand Practice")
    st.markdown("Ask the bot to generate a quiz on a specific topic. Grading happens locally to save API tokens.")
    
    quiz_topic = st.text_input("What should I quiz you on?", placeholder="e.g., Chapter 3, Photosynthesis, Thermodynamics...")
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        num_q = st.number_input("Questions", min_value=1, max_value=10, value=3)
    
    if st.button("Generate Quiz", type="primary"):
        if not st.session_state.db_ready:
            st.error("Please upload and process a document first.")
        elif not quiz_topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Analyzing text and generating questions..."):
                try:
                    db_manager = VectorStoreManager()
                    db = db_manager.load_vector_store()
                    pipeline = RAGPipeline(vector_store=db)
                    
                    quiz_json, docs = pipeline.generate_quiz(topic=quiz_topic, num_questions=num_q)
                    st.session_state.quiz_data = quiz_json
                    st.session_state.quiz_graded = False  # Reset grading state
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")

    # Render the Quiz Form if data exists
    if st.session_state.quiz_data:
        st.divider()
        with st.form("quiz_form"):
            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**{i+1}. {q['question']}**")
                # Using radio buttons for options
                user_answers[i] = st.radio(
                    "Select an option", 
                    options=q['options'], 
                    key=f"q_{i}", 
                    label_visibility="collapsed",
                    index=None  # Leave unselected initially
                )
                st.write("") # spacing

            submit_quiz = st.form_submit_button("Submit Answers")
            
            if submit_quiz:
                st.session_state.quiz_graded = True
                st.session_state.user_answers = user_answers

        # Render Results Locally (No LLM Call)
        if st.session_state.quiz_graded:
            st.subheader("Results")
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                selected = st.session_state.user_answers.get(i)
                correct_ans = q['answer']
                
                if selected == correct_ans:
                    score += 1
                    st.success(f"**Q{i+1}: Correct!**")
                    st.write(f"Explanation: {q['explanation']}")
                else:
                    st.error(f"**Q{i+1}: Incorrect.**")
                    st.write(f"Your answer: {selected}")
                    st.write(f"**Correct answer:** {correct_ans}")
                    st.write(f"Explanation: {q['explanation']}")
                st.divider()
            
            st.metric("Final Score", f"{score} / {len(st.session_state.quiz_data)}")