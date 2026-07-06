import streamlit as st
import os
from dotenv import load_dotenv

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.rag_pipeline import RAGPipeline

# Load API keys
load_dotenv()

st.set_page_config(page_title="AskMyBook", page_icon="📚", layout="centered")
st.title("📚 AskMyBook: Document Q&A")
st.markdown("Upload a textbook or handbook, and ask questions with exact page citations.")

# Setup directories
os.makedirs("data", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# Initialize Session State to track if DB is ready
if "db_ready" not in st.session_state:
    st.session_state.db_ready = os.path.exists("vectorstore/chroma.sqlite3")

with st.sidebar:
    st.header("1. Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    if st.button("Process Document") and uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Parsing and creating vector embeddings... (This may take a minute)"):
            processor = DocumentProcessor()
            pages = processor.load_pdf(file_path)
            chunks = processor.chunk_documents(pages)
            
            db_manager = VectorStoreManager()
            db_manager.create_vector_store(chunks)
            st.session_state.db_ready = True
            st.success("Document processed! Vector database updated.")

st.header("2. Ask Questions")
query = st.text_input("Ask a question about the document:")

if st.button("Submit Question"):
    if not st.session_state.db_ready:
        st.error("Please upload and process a document first.")
    elif not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching document and generating answer..."):
            try:
                db_manager = VectorStoreManager()
                db = db_manager.load_vector_store()
                
                pipeline = RAGPipeline(vector_store=db)
                answer, source_docs = pipeline.generate_answer(query)
                
                st.subheader("Answer:")
                st.write(answer)
                
                with st.expander("View Source Passages (Hybrid Search)"):
                    for i, doc in enumerate(source_docs):
                        page = doc.metadata.get('page', 'Unknown')
                        st.markdown(f"**Source {i+1} (Page {page}):**")
                        st.write(doc.page_content)
                        st.divider()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")