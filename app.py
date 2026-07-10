import os
import json
import streamlit as st
from dotenv import load_dotenv

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.rag_pipeline import RAGPipeline

# Load API keys
load_dotenv()

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="EduPulse AI - AskMyBook Studio", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom injection for professional CSS polish
st.markdown("""
    <style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Global Configurations ---
BASE_VECTOR_DIR = "vectorstores"
DATA_DIR = "data"
os.makedirs(BASE_VECTOR_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def get_cached_books():
    if not os.path.exists(BASE_VECTOR_DIR):
        return []
    return [d for d in os.listdir(BASE_VECTOR_DIR) if os.path.isdir(os.path.join(BASE_VECTOR_DIR, d))]

# --- 🚀 PERFORMANCE FIX: CACHE THE AI ENGINE IN MEMORY ---
# This prevents the app from re-loading HuggingFace Embeddings on every single click!
@st.cache_resource(show_spinner="Initializing AI Engine...")
def load_ai_engine(book_name):
    v_path = os.path.join(BASE_VECTOR_DIR, book_name)
    v_manager = VectorStoreManager(persist_directory=v_path)
    vector_store = v_manager.load_vector_store()
    rag_pipeline = RAGPipeline(vector_store=vector_store)
    return vector_store, rag_pipeline

# --- Initialize Core Session States ---
if "current_book" not in st.session_state:
    st.session_state.current_book = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_graded" not in st.session_state:
    st.session_state.quiz_graded = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {}

# --- Sidebar: Workspace & Document Lifecycle Management ---
with st.sidebar:
    # Fixed Brand Header
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <img src="https://img.icons8.com/fluency/48/education.png" width="40">
            <h2 style="margin: 0; font-size: 1.4rem;">EduPulse AI</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.caption("Advanced Academic RAG Environment")
    st.divider()
    
    st.subheader("📚 Book Workspace")
    cached_books = get_cached_books()
    
    workspace_mode = st.radio(
        "Workspace Source", 
        ["Select From Cache", "Process New Book"],
        index=0 if cached_books else 1
    )
    
    if workspace_mode == "Select From Cache" and cached_books:
        selected_book = st.selectbox("Choose a cached book:", cached_books)
        if st.button("🔌 Load Selected Workspace", use_container_width=True):
            st.session_state.current_book = selected_book
            st.session_state.messages = []  
            st.session_state.quiz_data = None
            st.session_state.quiz_graded = False
            st.session_state.user_answers = {}
            st.rerun()
    else:
        if workspace_mode == "Select From Cache":
            st.info("No cached workspaces found. Please upload a new book.")
            
        uploaded_file = st.file_uploader("Upload Book PDF", type=["pdf"])
        if uploaded_file is not None:
            safe_filename = uploaded_file.name.replace(" ", "_").replace(".", "_")
            target_vector_path = os.path.join(BASE_VECTOR_DIR, safe_filename)
            
            if st.button("⚡ Process & Index Book", use_container_width=True):
                with st.status("Ingesting text layers...", expanded=True) as status:
                    temp_path = os.path.join(DATA_DIR, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    status.update(label="Splitting document chunks...")
                    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
                    raw_pages = processor.load_pdf(temp_path)
                    chunks = processor.chunk_documents(raw_pages)
                    
                    status.update(label="Generating BGE semantic embeddings...")
                    v_manager = VectorStoreManager(persist_directory=target_vector_path)
                    v_manager.create_vector_store(chunks)
                    
                    st.session_state.doc_stats[safe_filename] = {
                        "pages": len(raw_pages),
                        "chunks": len(chunks),
                        "filename": uploaded_file.name
                    }
                    
                    status.update(label="Workspace compiled!", state="complete")
                    
                st.session_state.current_book = safe_filename
                st.session_state.messages = []
                st.session_state.quiz_data = None
                st.session_state.quiz_graded = False
                st.session_state.user_answers = {}
                st.rerun()

    st.divider()
    st.subheader("⚙️ Engine Parameters")
    st.session_state.memory_window = st.slider("Chat Context Window", min_value=2, max_value=10, value=4)

# --- Main Application Shell ---
if not st.session_state.current_book:
    st.info("👋 Welcome! Please select a cached book workspace or upload a new textbook in the sidebar to begin.")
else:
    active_name = st.session_state.current_book.replace("_pdf", ".pdf").replace("_", " ")
    st.subheader(f"📖 Active Workspace: {active_name}")
    
    # ⚡ Load the AI models instantly using Streamlit Cache ⚡
    try:
        vector_store, rag_pipeline = load_ai_engine(st.session_state.current_book)
    except Exception as e:
        st.error(f"Error initializing AI engine: {e}")
        st.stop()
        
    tab_chat, tab_quiz, tab_analytics = st.tabs([
        "💬 Interactive Study Chat", 
        "📝 Real-time Practice Quiz", 
        "📊 Document Insights & Analytics"
    ])
    
    # ==========================================
    # TAB 1: INTERACTIVE STUDY CHAT
    # ==========================================
    with tab_chat:
        st.markdown("#### Conversational Deep-Dive")
        
        chat_container = st.container(height=450, border=True)
        
        with chat_container:
            if not st.session_state.messages:
                st.caption("_No messages exchanged yet. Ask a specific question down below to engage the book context._")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        if user_query := st.chat_input("Ask a question about your book..."):
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_query)
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            with st.spinner("Analyzing text pages..."):
                try:
                    history_context = ""
                    recent_turns = st.session_state.messages[-st.session_state.memory_window:]
                    for turn in recent_turns[:-1]:
                        history_context += f"{turn['role'].capitalize()}: {turn['content']}\n"
                    
                    retriever = rag_pipeline._setup_hybrid_retriever(search_kwargs={"k": 4})
                    retrieved_docs = retriever.invoke(user_query)
                    
                    context_str = "\n\n".join([
                        f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" 
                        for doc in retrieved_docs
                    ])
                    
                    # 🚀 FIX: Strict instruction added to block JSON formatting
                    prompt = f"""
                    You are an expert AI Study Assistant. Answer the user's question accurately using ONLY the context provided below.
                    
                    CRITICAL INSTRUCTION: Provide your answer in conversational, readable Markdown text. 
                    DO NOT output JSON. DO NOT format your response as a JSON array or object.
                    
                    Conversational History Context:
                    {history_context}
                    
                    Document Source Context:
                    {context_str}
                    
                    Question: {user_query}
                    Answer:
                    """
                    
                    response = rag_pipeline.llm.invoke(prompt)
                    bot_response = response.content
                    
                except Exception as e:
                    bot_response = f"⚠️ RAG Pipeline Error encountered: {str(e)}"
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.rerun()

    # ==========================================
    # TAB 2: REAL-TIME PRACTICE QUIZ
    # ==========================================
    with tab_quiz:
        st.markdown("#### Synthetic Knowledge Assessment")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            quiz_topic = st.text_input("Enter target topic focus:", placeholder="e.g., Database Indexing")
        with c2:
            quiz_count = st.slider("Question Count", min_value=2, max_value=8, value=3)
            
        if st.button("🔥 Generate Practice Quiz", use_container_width=True):
            if not quiz_topic.strip():
                st.warning("Please specify a topic.")
            else:
                with st.spinner("Synthesizing questions..."):
                    try:
                        quiz_data, _ = rag_pipeline.generate_quiz(topic=quiz_topic, num_questions=quiz_count)
                        st.session_state.quiz_data = quiz_data
                        st.session_state.quiz_graded = False
                        st.session_state.user_answers = {}
                        st.rerun()
                    except Exception as e:
                        st.error(f"Quiz Generation Failure: {e}")
                        
        st.divider()
        
        if st.session_state.quiz_data:
            with st.form(key="quiz_evaluation_form"):
                current_answers = {}
                
                for i, q in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    
                    saved_choice = st.session_state.user_answers.get(i, None)
                    default_idx = q['options'].index(saved_choice) if saved_choice in q['options'] else None
                    
                    chosen_option = st.radio(
                        f"Select Option for Q{i+1}",
                        options=q['options'],
                        index=default_idx,
                        key=f"mcq_radio_{i}",
                        label_visibility="collapsed"
                    )
                    current_answers[i] = chosen_option
                    
                    if st.session_state.quiz_graded:
                        user_ans = st.session_state.user_answers.get(i)
                        correct_ans = q['answer']
                        
                        if user_ans == correct_ans:
                            st.success(f"✨ **Correct!**")
                        else:
                            st.error(f"❌ **Incorrect Selection**")
                            st.markdown(f"* **Correct Answer:** `{correct_ans}`")
                        
                        st.info(f"💡 **Explanation:** {q['explanation']}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if not st.session_state.quiz_graded:
                    if st.form_submit_button("🏁 Submit Answers for Review", use_container_width=True):
                        st.session_state.user_answers = current_answers
                        st.session_state.quiz_graded = True
                        st.rerun()
                else:
                    if st.form_submit_button("🔄 Clear Review State & Re-take", use_container_width=True):
                        st.session_state.quiz_graded = False
                        st.session_state.user_answers = {}
                        st.rerun()
                        
            if st.session_state.quiz_graded:
                total = len(st.session_state.quiz_data)
                correct_count = sum([1 for i, q in enumerate(st.session_state.quiz_data) if st.session_state.user_answers.get(i) == q['answer']])
                score_pct = int((correct_count / total) * 100)
                
                if score_pct >= 70:
                    st.balloons()
                st.metric(label="Overall Performance Rating", value=f"{correct_count} / {total}", delta=f"{score_pct}% Mastery")

    # ==========================================
    # TAB 3: DOCUMENT INSIGHTS
    # ==========================================
    with tab_analytics:
        st.markdown("#### Deep Vector Database Insights")
        
        col1, col2, col3 = st.columns(3)
        try:
            db_data = vector_store.get()
            total_db_chunks = len(db_data.get('documents', []))
        except:
            total_db_chunks = "N/A"
            
        stats = st.session_state.doc_stats.get(st.session_state.current_book, {"pages": "Active", "chunks": total_db_chunks})
        
        with col1:
            st.markdown(f"<div class='metric-card'>🛸 <b>Indexing Mode</b><br><h2>Hybrid RAG</h2><small>Dense + BM25</small></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'>📄 <b>Document Length</b><br><h2>{stats.get('pages', 'Active')}</h2><small>Total Raw Text Pages</small></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'>🧩 <b>Database Nodes</b><br><h2>{total_db_chunks}</h2><small>Calculated Source Chunks</small></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 🔍 Embedded Workspace Data Preview")
        
        if total_db_chunks != "N/A" and total_db_chunks > 0:
            preview_limit = min(5, total_db_chunks)
            for index in range(preview_limit):
                with st.expander(f"Chunk Node #{index + 1} - Source: Page {db_data['metadatas'][index].get('page', 'Unknown')}"):
                    st.text_area("Chunk Content Preview", value=db_data['documents'][index], height=120, disabled=True, key=f"chunk_text_{index}")
        else:
            st.info("No chunk logs could be extracted.")