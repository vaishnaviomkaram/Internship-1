import os
import time
import streamlit as st
from dotenv import load_dotenv

# Modular imports
from src.ingest import DocumentIngestor
from src.chunk import DocumentChunker
from src.embed import EmbeddingManager
from src.retrieve import RetrievalEngine
from src.generate import RAGGenerator
from src.compare import DocumentComparator
from src.eval import RAGEvaluator

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]


st.set_page_config(page_title="StudyBuddy AI (I2)", page_icon="🎓", layout="wide")

BASE_VECTOR_DIR = "vectorstores"
DATA_DIR = "data"
os.makedirs(BASE_VECTOR_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ==========================================
# ISOLATED SESSION STATE
# ==========================================
# Each mode gets its own dictionary for vector paths to prevent cross-mode leakage
modes = ["chat", "compare", "quiz", "eval"]
for mode in modes:
    if f"{mode}_paths" not in st.session_state: st.session_state[f"{mode}_paths"] = {}
    
if "chat_messages" not in st.session_state: st.session_state.chat_messages = []
if "compare_messages" not in st.session_state: st.session_state.compare_messages = []
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state: st.session_state.quiz_submitted = False
if "user_answers" not in st.session_state: st.session_state.user_answers = {}

# ==========================================
# HELPER: PROCESS & INDEX
# ==========================================
def process_files(files, mode_key):
    processed_count = 0
    for up_file in files:
        safe_name = up_file.name.replace(" ", "_").replace(".pdf", "")
        target_vector_path = os.path.join(BASE_VECTOR_DIR, safe_name)
        
        # Register to this specific mode's memory
        if safe_name not in st.session_state[f"{mode_key}_paths"]:
            # Only do heavy lifting if not on disk
            if not os.path.exists(target_vector_path):
                with st.status(f"Processing {up_file.name}...", expanded=True) as status:
                    temp_path = os.path.join(DATA_DIR, up_file.name)
                    with open(temp_path, "wb") as f: f.write(up_file.getbuffer())
                    status.update(label="Extracting text...")
                    raw_pages = DocumentIngestor().parse_pdf(temp_path)
                    status.update(label="Chunking...")
                    chunks = DocumentChunker().chunk_pages(raw_pages)
                    status.update(label="Embedding...")
                    EmbeddingManager(persist_directory=target_vector_path).create_vector_store(chunks)
                    status.update(label="Done!", state="complete")
                    
            st.session_state[f"{mode_key}_paths"][safe_name] = target_vector_path
            processed_count += 1
            
    if processed_count > 0:
        st.success(f"✅ Indexed {processed_count} doc(s) for {mode_key.upper()}!")
        time.sleep(1.5)
        st.rerun()
    elif len(files) > 0:
        st.info("Already indexed for this mode.")

# ==========================================
# SIDEBAR: NAVIGATION & UPLOADS
# ==========================================
with st.sidebar:
    st.title("🎓 StudyBuddy AI")
    st.caption("Strictly isolated workspaces.")
    st.divider()
    
    # Navigation Menu
    mode = st.radio(
        "Select Workspace",
        ["💬 Chat", "⚖️ Compare", "📝 Quiz", "🎯 Eval"],
        label_visibility="collapsed",
        horizontal=False
    )
    
    st.divider()
    
    # Dynamic Uploaders based on Mode
    if mode == "💬 Chat":
        st.subheader("📂 Chat Library")
        chat_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, key="chat_up")
        if st.button("✨ Process & Index", key="btn_chat", disabled=not chat_files, use_container_width=True):
            process_files(chat_files, "chat")
            
    elif mode == "⚖️ Compare":
        st.subheader("⚖️ Comparison Setup")
        c1, c2 = st.columns(2)
        with c1: f_x = st.file_uploader("Doc X", type=["pdf"], key="comp_x")
        with c2: f_y = st.file_uploader("Doc Y", type=["pdf"], key="comp_y")
        if st.button("✨ Process Both", key="btn_comp", disabled=not (f_x and f_y), use_container_width=True):
            process_files([f for f in [f_x, f_y] if f], "compare")
            
    elif mode == "📝 Quiz":
        st.subheader("📂 Quiz Source")
        quiz_file = st.file_uploader("Upload Textbook", type=["pdf"], key="quiz_up")
        if st.button("✨ Process & Index", key="btn_quiz", disabled=not quiz_file, use_container_width=True):
            process_files([quiz_file], "quiz")
            
    elif mode == "🎯 Eval":
        st.subheader("📂 Eval Source")
        eval_file = st.file_uploader("Upload Textbook", type=["pdf"], key="eval_up")
        if st.button("✨ Process & Index", key="btn_eval", disabled=not eval_file, use_container_width=True):
            process_files([eval_file], "eval")

    st.divider()
    
    # Active Library Display
    st.subheader("📚 Active Docs")
    current_paths = st.session_state.get(f"{mode.split()[-1].lower().strip('💬⚖️📝🎯')}_paths", {})
    # Clean key extraction for display
    clean_mode = mode.split()[-1].lower()
    if clean_mode not in st.session_state: 
        # Fallback mapping
        mapping = {"💬 Chat": "chat", "⚖️ Compare": "compare", "📝 Quiz": "quiz", "🎯 Eval": "eval"}
        clean_mode = mapping.get(mode, "chat")
        
    active_docs = st.session_state[f"{clean_mode}_paths"].keys()
    if active_docs:
        for doc in active_docs:
            st.markdown(f"✅ **{doc.replace('_', ' ')}**")
    else:
        st.info("No documents active.")
        
    st.divider()
    if st.button("🔄 Reset Workspace", use_container_width=True):
        st.session_state[f"{clean_mode}_paths"] = {}
        if clean_mode == "chat": st.session_state.chat_messages = []
        if clean_mode == "compare": st.session_state.compare_messages = []
        if clean_mode == "quiz": 
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
        st.rerun()

# ==========================================
# MAIN CONTENT AREA
# ==========================================

# --- MODE 1: CHAT ---
if mode == "💬 Chat":
    st.header("💬 Document Q&A")
    if not st.session_state.chat_paths:
        st.info("👈 Please upload and process a document in the sidebar to start chatting.")
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("Ask a question..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    docs = []
                    active_books = list(st.session_state.chat_paths.keys())
                    k_per_book = max(2, 6 // len(active_books))
                    for book in active_books:
                        v_path = st.session_state.chat_paths[book]
                        vs = EmbeddingManager(persist_directory=v_path).load_vector_store()
                        retriever = RetrievalEngine(vs).get_hybrid_retriever(k=k_per_book)
                        docs.extend(retriever.invoke(prompt))
                    
                    docs = docs[:6] 
                    context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in docs])
                    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_messages[-4:-1]])
                    generator = RAGGenerator()
                    answer = generator.generate_answer(prompt, context, history)
                    st.markdown(answer)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

# --- MODE 2: COMPARE ---
elif mode == "⚖️ Compare":
    st.header("⚖️ X vs Y Comparison")
    if len(st.session_state.compare_paths) != 2:
        st.info("👈 Please upload and process **exactly two** documents in the sidebar to compare.")
    else:
        books = list(st.session_state.compare_paths.keys())
        st.caption(f"Comparing: **{books[0].replace('_', ' ')}** vs **{books[1].replace('_', ' ')}**")
        
        for msg in st.session_state.compare_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("What's the difference regarding...?"):
            st.session_state.compare_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Comparing..."):
                    v1_path = st.session_state.compare_paths[books[0]]
                    v2_path = st.session_state.compare_paths[books[1]]
                    vs1 = EmbeddingManager(persist_directory=v1_path).load_vector_store()
                    vs2 = EmbeddingManager(persist_directory=v2_path).load_vector_store()
                    r1 = RetrievalEngine(vs1).get_hybrid_retriever(k=3)
                    r2 = RetrievalEngine(vs2).get_hybrid_retriever(k=3)
                    docs1, docs2 = r1.invoke(prompt), r2.invoke(prompt)
                    ctx1 = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in docs1])
                    ctx2 = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in docs2])
                    
                    generator = RAGGenerator()
                    comparator = DocumentComparator(generator.llm)
                    comp_answer = comparator.compare(prompt, ctx1, books[0], ctx2, books[1])
                    st.markdown(comp_answer)
            st.session_state.compare_messages.append({"role": "assistant", "content": comp_answer})
            st.rerun()

# --- MODE 3: QUIZ ---
elif mode == "📝 Quiz":
    st.header("📝 Practice Quiz")
    if not st.session_state.quiz_paths:
        st.info("👈 Please upload and process a textbook in the sidebar.")
    else:
        q_name = list(st.session_state.quiz_paths.keys())[0]
        st.caption(f"Source: **{q_name.replace('_', ' ')}**")
        
        col1, col2 = st.columns([3, 1])
        with col1: topic = st.text_input("Topic:")
        with col2: num_q = st.number_input("Questions", 1, 10, 3)
            
        if st.button("Generate Quiz", use_container_width=True):
            if topic:
                with st.spinner("Generating..."):
                    v_path = st.session_state.quiz_paths[q_name]
                    vs = EmbeddingManager(persist_directory=v_path).load_vector_store()
                    retriever = RetrievalEngine(vs).get_hybrid_retriever(k=5)
                    docs = retriever.invoke(topic)
                    context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in docs])
                    generator = RAGGenerator()
                    try:
                        quiz_res = generator.generate_quiz(topic, context, int(num_q))
                        if isinstance(quiz_res, dict) and "error" in quiz_res:
                            st.warning(quiz_res["error"])
                        else:
                            st.session_state.quiz_data = quiz_res
                            st.session_state.user_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        if st.session_state.quiz_data and isinstance(st.session_state.quiz_data, list):
            st.divider()
            with st.form("quiz_form"):
                selections = {}
                correct = 0
                for i, q in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    user_ans = st.session_state.user_answers.get(i) if st.session_state.get("quiz_submitted") else None
                    chosen = st.radio(
                        f"Opt {i}", options=q['options'], key=f"q_{i}", label_visibility="collapsed",
                        index=q['options'].index(user_ans) if user_ans in q['options'] else None,
                        disabled=st.session_state.get("quiz_submitted", False)
                    )
                    selections[i] = chosen
                    
                    if st.session_state.get("quiz_submitted"):
                        if user_ans == q['answer']:
                            st.success("✅ Correct!")
                            correct += 1
                        else:
                            st.error(f"❌ Incorrect. You chose: {user_ans}")
                        with st.expander("Explanation", expanded=True):
                            st.info(f"**Ans:** {q['answer']}\n\n**Why:** {q['explanation']}")
                    st.markdown("---")
                    
                if not st.session_state.get("quiz_submitted"):
                    if st.form_submit_button("Submit", use_container_width=True):
                        valid = {k: v for k, v in selections.items() if v}
                        if len(valid) < len(st.session_state.quiz_data):
                            st.warning("Answer all questions.")
                        else:
                            st.session_state.user_answers = valid
                            st.session_state.quiz_submitted = True
                            st.rerun()
                else:
                    st.metric("Score", f"{correct}/{len(st.session_state.quiz_data)}")
                    if st.form_submit_button("Reset", use_container_width=True):
                        st.session_state.quiz_data = None
                        st.session_state.quiz_submitted = False
                        st.rerun()

# --- MODE 4: EVAL ---
elif mode == "🎯 Eval":
    st.header("🎯 RAG Evaluation")
    if not st.session_state.eval_paths:
        st.info("👈 Please upload and process a textbook in the sidebar.")
    else:
        e_name = list(st.session_state.eval_paths.keys())[0]
        st.caption(f"Source: **{e_name.replace('_', ' ')}**")
        eval_q = st.text_input("Test Question:", value="Summarize chapter 1.")
        if st.button("Run Eval", use_container_width=True):
            v_path = st.session_state.eval_paths[e_name]
            vs = EmbeddingManager(persist_directory=v_path).load_vector_store()
            retriever = RetrievalEngine(vs).get_hybrid_retriever(k=4)
            docs = retriever.invoke(eval_q)
            context = "\n\n".join([f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}" for doc in docs])
            generator = RAGGenerator()
            evaluator = RAGEvaluator(generator.llm)
            with st.spinner("Evaluating..."):
                ans = generator.generate_answer(eval_q, context)
                st.info(ans)
                scores = evaluator.evaluate_response(eval_q, ans, context)
                c1, c2, c3 = st.columns(3)
                c1.metric("Correctness", f"{scores['correctness_score']}/5")
                c2.metric("Citation", f"{scores['citation_score']}/5")
                c3.metric("Complete", f"{scores['completeness_score']}/5")
                st.markdown(f"**Feedback:** {scores['feedback']}")
