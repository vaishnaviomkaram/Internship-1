
# 📚 AskMyBook: AI-Powered Document Q&A System

> *An intelligent, context-aware document assistant that uses Retrieval-Augmented Generation (RAG) to deliver precise, citation-backed answers from isolated PDF corpora.*

**Author:** Vaishnavi  
**Segment:** Foundations of Applied Machine Learning  
**Problem Statement Code:** I2 (Document Q&A — RAG over a Focused Corpus)

---

## 🎥 Demo
| Description | Link |
| :--- | :--- |
| **Live Deployment:** | [Streamlit app](https://internship-1-fvhaqdvziykwpnsat2m92u.streamlit.app/)|
| **Walkthrough Video (3-5 min):** | [Video Link](https://)|

---

## 🎯 Problem Statement

Manually searching through massive academic textbooks, research papers, or regulatory manuals is highly inefficient. Traditional keyword indexing misses semantic context and intent, while generic Large Language Models (LLMs) frequently hallucinate information when answering domain-specific questions.

**AskMyBook** solves this by bridging the gap between static documents and generative AI. It converts long-form PDFs into a highly structured local vector index. When a user asks a question, the system uses a dual-layer hybrid search mechanism to retrieve the most relevant text chunks and forces the LLM to answer *only* using that retrieved context, strictly enforcing inline page citations. The application supports four distinct modes: single-document Q&A chat, multi-document comparison, auto-generated practice quizzes, and LLM-as-Judge evaluation of responses.

---

## 🏗️ Architecture Diagram

![Architecture Diagram](docs/architecture.png)


```mermaid
graph TD
    A[PDF Upload] --> B[PyMuPDF Page Extractor]
    B --> C[Metadata Tagging: Filename + Page Number]
    C --> D[LangChain Recursive Character Text Splitter]
    D --> E[(Chroma Local Vector DB)]
    D --> F[(BM25 Keyword Index)]
    
    G[User Query via Streamlit UI] --> H[Memory Window Context]
    H --> I[Hybrid Ensemble Retriever]
    E -->|Dense Vectors| I
    F -->|Sparse Vectors| I
    I --> J[Retrieved Context with Source Pages]
    J --> K[Gemini 3.1 Flash Lite LLM]
    K --> L[Structured Answer with Inline Citations]
```

---

## 🛠️ Technology Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Language** | Python 3.10+ | Ecosystem standard for data pipelines and machine learning. |
| **PDF Extraction** | PyMuPDF (`fitz`) | High-speed, granular extraction perfect for attaching 1-indexed page numbers. |
| **Chunking** | LangChain Text Splitters | `RecursiveCharacterTextSplitter` preserves semantic blocks and paragraph structures. |
| **Embeddings** | HuggingFace (`BAAI/bge-small-en-v1.5`) | Lightweight, highly accurate local open-source embeddings with zero API costs. |
| **Vector DB** | Chroma | Developer-friendly local persistence engine optimized for metadata filtering. |
| **Retriever** | EnsembleRetriever (BM25 + Dense) | Combines 50% dense vector search (semantic) with 50% BM25 (sparse keyword) for best recall. |
| **LLM Engine** | Gemini 3.1 Flash Lite | Ultra-low latency, generous free tier, and exceptional at following strict guardrails and JSON formatting. |
| **Frontend UI** | Streamlit | Rapid prototyping for data applications with built-in session state management. |
| **Testing** | pytest with unittest.mock | Standard Python testing framework with mocking for isolated unit tests. |

---

## 🏁 Quickstart

### Prerequisites
- Python 3.10 or higher
- Git
- A Google Gemini API key (get one free at [Google AI Studio](https://aistudio.google.com/apikey))

### 1. Clone and Install
```bash
git clone https://github.com/vaishnaviomkaram/Internship-1.git
cd Internship-1
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root with your Gemini API key:
```bash
echo 'GOOGLE_API_KEY="your_api_key_here"' > .env
```

For Streamlit Cloud deployment, add `GOOGLE_API_KEY` in the app's Secrets management panel.

### 3. Run the Application
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`. Use the sidebar to:
- Upload PDFs in any of the four modes (Chat, Compare, Quiz, Eval)
- Click "Process & Index" to build the vector store
- Start asking questions, comparing documents, generating quizzes, or evaluating responses

### 4. Run Tests
```bash
python -m pytest tests/ -v
```
Expected output:
<img width="1147" height="263" alt="image" src="https://github.com/user-attachments/assets/6ffcda40-8079-4fdd-b4ef-838b839493de" />


---

## 📚 Data Sources

The application accepts any text-heavy PDF document. For testing and demonstration purposes, a sample textbook PDF is placed in `data/sample_textbook.pdf`. The system is optimized for:
- Academic textbooks with clear chapter/section structure
- Research papers with proper text formatting
- College handbooks and syllabus documents
- Regulatory or policy manuals

**Current limitation:** Scanned documents and image-based PDFs are not supported in this version. Complex tables and mathematical equations may lose formatting fidelity during extraction.

---

## 📄 Architecture Decision Records (ADRs)

All major architectural decisions are documented as ADRs in the `/docs/adr/` directory:

| ADR | Title | Summary |
|-----|-------|---------|
| [ADR-001](docs/adr/ADR-001.md) | External Gemini API for Text Generation with Local Embeddings | Why we split processing: local HuggingFace embeddings for cost-free vectorization, cloud Gemini API for high-quality text generation |
| [ADR-002](docs/adr/ADR-002.md) | Hybrid Retrieval Strategy — BM25 + Dense Embeddings Ensemble | Why combining semantic search with keyword search at 50/50 weights gives the best retrieval accuracy for textbook Q&A |
| [ADR-003](docs/adr/ADR-003.md) | Isolated Workspace State Management in Streamlit | How we prevent cross-mode data leakage by namespace-isolating session state for Chat, Compare, Quiz, and Eval modes |

Each ADR includes: Context, Decision, Consequences (positive and negative), Alternatives Considered, and relevant diagrams.

---

## 🚀 Mini-Extension: Compare Two Documents

### What It Is
The Compare mode allows users to upload two separate PDF documents and ask comparative questions like "What's the difference between these two on topic X?" or "How does Document A's approach differ from Document B's regarding concept Y?"

### How It Works
1. Upload two PDFs in the Compare workspace sidebar
2. Click "Process Both" to index them into separate vector stores
3. Ask a comparative question in the chat interface
4. The system retrieves relevant chunks from both documents independently
5. A specialized comparator prompt forces the LLM to analyze both contexts side-by-side, citing sources from each document with proper attribution (e.g., "Doc 1, Page 3" vs "Doc 2, Page 7")

### Why I Added It
Multi-document reasoning is a significant step up from single-document RAG. It demonstrates the ability to:
- Manage multiple isolated vector stores simultaneously
- Construct prompts that enforce cross-document comparison without hallucination
- Handle conflicting or complementary information from separate sources
- Attribute every claim to the correct source document with page-level precision

This feature directly previews the "enterprise mess" extension path described in the 3rd year roadmap, where the system would handle 4+ heterogeneous source types.

---

## ⚠️ Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Text-only PDFs** | Scanned documents, image-based PDFs, and handwritten notes cannot be processed | Use OCR-preprocessed PDFs; OCR support is planned for 3rd year extension |
| **Gemini API rate limits** | Free tier has daily quotas on text generation requests; heavy testing may hit limits | Local embeddings have no limits; generation quota is generous (~1500 requests/day on free tier) |
| **Vector store append-only** | Re-processing a modified PDF appends new chunks to the existing vector store rather than replacing them | Use the "Reset Workspace" button in sidebar or manually delete the `vectorstores/` directory |
| **No persistent chat history** | Refreshing the browser or restarting the Streamlit server loses all chat history and quiz progress | This is by design for the MVP; persistent storage would require a database backend |
| **Single LLM provider** | If Gemini API experiences downtime, all generation features stop working | The retrieval layer remains functional; a fallback provider could be added in 3rd year |
| **Large document memory** | Very large PDFs (500+ pages) may cause slower initial processing and higher memory usage | Chunking parameters (1000 tokens, 200 overlap) are optimized for typical textbooks |

---

## 🧠 What I Learned

### Week 3: Multi-Mode Architecture, Testing, and Deployment

- **Isolated State Management in Streamlit:** I learned that Streamlit's reactive execution model (rerunning the entire script on every interaction) demands careful state architecture. When I encountered a bug where switching between Chat and Compare modes mixed up chat histories, I realized I needed namespace-isolated session state dictionaries (`chat_paths`, `compare_paths`, etc.). Each mode now has its own clean bubble of state that doesn't leak across workspaces.

- **Hybrid Retrieval Actually Works Better:** Following up on my Week 1 mentor question about optimal weights, I implemented the EnsembleRetriever with 50/50 BM25-to-dense split and tested it extensively. The difference was immediately noticeable: pure dense search would miss exact terminology queries, while BM25 alone couldn't handle conceptual paraphrasing. The hybrid approach catches both, and the equal weighting turned out to be the sweet spot without needing complex tuning.

- **LLM-as-Judge Requires Strict Prompting:** Building the evaluation module taught me that LLMs are surprisingly good at grading their own outputs—but only if the prompt is airtight. I had to explicitly force the correctness score to 1 if *any* outside knowledge appears, and use JSON-only output instructions. Even then, the model sometimes wraps JSON in markdown backticks, so I built a robust cleanup pipeline.

- **Prompt Engineering is Defense in Depth:** Every guardrail I added (no code generation, refuse out-of-context questions, strict citation formatting) had to be reinforced across all four prompts (chat, compare, quiz, eval). One weak prompt is enough for hallucination to slip through. The quiz prompt now explicitly returns an error dictionary if the topic isn't in the textbook, and the comparator refuses to discuss anything not in either document.

- **Testing PDF Pipelines Needs Mocking:** Writing tests for `ingest.py` taught me the importance of mocking external dependencies. I couldn't rely on a real PDF file being present in the test environment, so I used `unittest.mock` to fake both `os.path.exists` and `fitz.open`. This let me verify the metadata extraction logic, page numbering, and file-not-found error handling without any actual PDFs.

- **Deployment Teaches You What You Skipped:** Deploying on Streamlit Cloud forced me to confront all my hardcoded assumptions—file paths that worked locally broke in the cloud, the `.env` file wasn't uploaded, and the Chroma persistence directory needed write permissions. The "it works on my machine" to "it works in production" gap is real, and going through it once made me much more careful about configuration management.

### Week 2: UI, State Management, and API Trade-offs

- **Reactive UIs and Session State:** Building the frontend taught me that Streamlit reruns the script from top to bottom on every user interaction. I learned to use `st.session_state` to persist variables like the `messages` array, `memory_window`, and `db_ready` flags. This ensures users can chat concurrently and adjust settings without losing their previous conversation context or vector database connections.

- **Conversational Context in RAG:** I learned that single-turn RAG is insufficient for a seamless "buddy" experience. I updated the `PromptTemplate` to include a `{chat_history}` variable. By dynamically slicing the `st.session_state.messages` array based on a user-defined memory window and passing it as a formatted string, the LLM can accurately understand follow-up questions.

- **Enforcing JSON Outputs for UI Components:** For the quiz generation mini-extension, I learned how to instruct the LLM to act as a strict teacher and return *only* a valid JSON array of questions, options, and explanations. Because LLMs stubbornly wrap JSON in markdown blocks, I implemented `.replace('```json', '')` as a fallback cleanup mechanism. The Streamlit UI then parses this JSON to render radio buttons and grade the user locally, saving additional API tokens.

- **Architectural Trade-offs (Local vs. Cloud):** I learned the realities of resource constraints during rapid prototyping. I split the processing load into a hybrid model:

| Task | Component Used | Execution Location | Why I Learned This Trade-off |
|------|----------------|--------------------|------------------------------|
| **Embeddings** | HuggingFace (`BAAI/bge-small-en-v1.5`) | Local | Saves API costs and executes quickly on local hardware for vector math. |
| **Vector Store** | Chroma | Local Disk | Persistent directories allow skipping the parsing phase on subsequent runs. |
| **Text Generation** | Gemini 3.1 Flash Lite | Cloud API | Prevents local VRAM crashes and executes JSON instructions flawlessly, though it requires managing API rate limits. |

### Week 1: Data Ingestion & Retrieval Strategy

- **Citation Integrity Requires Early Mapping:** I learned that tracking inline citations downstream depends entirely on preserving document structures immediately during ingestion. By injecting 1-indexed page markers directly into the raw dictionary layers using `fitz` (PyMuPDF), I ensured that when the text is split later, every single child chunk inherits its exact parent page number.

- **Semantic Boundaries > Arbitrary Cutoffs:** I initially thought chunking just meant splitting text every 1,000 characters. By implementing LangChain's `RecursiveCharacterTextSplitter`, I learned how to cascade through structural delimiters (`\n\n`, then `\n`, then spaces) to minimize semantic fracture.

- **The Pitfalls of "Dirty" Document Layouts:** Real-world PDFs are messy. They contain blank pages, weird structural layouts, and invisible whitespace characters. I learned that introducing strict `.strip()` validation and skipping empty pages during the extraction phase prevents empty or useless chunks from bloating the vector index.

- **Modularization and Local Persistence:** Moving from a single massive script to a modular architecture made testing infinitely easier. Furthermore, pivoting to **Chroma** taught me how local vector persistence works (`persist_directory="./vectorstore"`).

- **The Necessity of Hybrid Retrieval:** I realized that pure vector similarity (Dense search via BGE-Small) is great for conceptual questions but terrible at finding specific variable names or exact terminology. Wiring up the LangChain `EnsembleRetriever` taught me how to marry dense semantic search with sparse lexical search (`BM25Retriever`) utilizing balanced 0.5/0.5 weights to get the best of both worlds.

---

## 🔭 What I'd Do in 3rd Year

See my [3rd Year Extension Roadmap](docs/roadmap_3rd_year.md) for a detailed plan covering:
- Semester 5 (Aug-Dec 2026): Adding OCR support, multi-format ingestion, and persistent user sessions
- Semester 6 (Jan-May 2027): Fine-tuning a small domain-specific model, adding agentic query decomposition
- 3rd Year Internship (Jun-Jul 2027): Scaling to enterprise document corpora (E3 problem statement)

---

## 📜 License & Acknowledgements

Built as part of the **2nd Year B.Tech CSE-AIDE Internship Program (2026)** — Foundations of Applied Machine Learning.

**Acknowledgements:**
- LangChain and Chroma communities for excellent RAG documentation
- HuggingFace for open-source embedding models
- Google Generative AI for the Gemini API free tier
- Streamlit for the rapid prototyping framework
```
