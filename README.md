# 📚 AskMyBook: AI-Powered Document Q&A System

> *An intelligent, context-aware document assistant that uses Retrieval-Augmented Generation (RAG) to deliver precise, citation-backed answers from isolated PDF corpora.*

**Author:** Vaishnavi  
**Segment:** Foundations of Applied Machine Learning  
**Problem Statement Code:** I2 (Document Q&A — RAG over a Focused Corpus)  

---

## 🧠 What I Learned This Week

* **Citation Integrity Requires Early Mapping:** I learned that tracking inline citations downstream depends entirely on preserving document structures immediately during ingestion. By injecting 1-indexed page markers directly into the raw dictionary layers using `PyMuPDF` (on Tuesday), I ensured that when the text is split later, every single child chunk inherits its exact parent page number.
* **Semantic Boundaries > Arbitrary Cutoffs:** I initially thought chunking just meant splitting text every 1,000 characters. By implementing LangChain's `RecursiveCharacterTextSplitter` (on Wednesday), I learned how to cascade through structural delimiters (`\n\n`, then `\n`, then spaces). This minimizes semantic fracture—keeping full paragraphs and sentences together so the embedding model actually understands the context.
* **The Pitfalls of "Dirty" Document Layouts:** Real-world PDFs are messy. They contain blank pages, weird structural layouts, and invisible whitespace characters. I learned that introducing strict `.strip()` validation and skipping empty pages during the extraction phase prevents empty or useless chunks from bloating the vector index.
* **Modularization and Local Persistence:** Moving from a single massive script to a modular architecture (`document_processor.py`, `vector_store.py`, `rag_pipeline.py`) made testing infinitely easier. Furthermore, pivoting to **ChromaDB** taught me how local vector persistence works. Instead of re-embedding the document every time the script runs, the data is stored locally and simply retrieved, saving massive amounts of compute time.
* **The Necessity of Hybrid Retrieval:** I realized that pure vector similarity (Dense search via BGE-Small) is great for conceptual questions but terrible at finding specific variable names or exact terminology. Wiring up the LangChain `EnsembleRetriever` taught me how to marry dense semantic search with sparse lexical search (BM25) to get the best of both worlds.


---

## 🔗 Live Links & Demos

* **Live Deployment URL:** *[To be added in Week 4]*
* **Loom Walkthrough:** *[To be added in Week 4]*

---

## 🎯 Problem Statement

Manually searching through massive academic textbooks, research papers, or regulatory manuals is highly inefficient. Traditional keyword indexing misses semantic context and intent, while generic Large Language Models (LLMs) frequently hallucinate information when answering domain-specific questions.

**AskMyBook** solves this by bridging the gap between static documents and generative AI. It converts long-form PDFs into a highly structured local vector index. When a user asks a question, the system uses a dual-layer hybrid search mechanism to retrieve the most relevant text chunks and forces the LLM to answer *only* using that retrieved context, strictly enforcing inline page citations.

---

## 🏗️ Architecture Diagram

```text
[PDF Upload] ➔ [PyMuPDF Page Extractor] ➔ [Metadata Tagging (Filename + Page #)]
                                                    │
                                                    ▼
[User UI] ➔ [Query Vector]            [LangChain Recursive Text Splitting]
    │             │                                 │
    ▼             ▼                                 ▼
[Answer] ◀─ [Gemini LLM] ◀─ [Ensemble Retriever (Chroma Dense + BM25 Sparse)]

```



# Document QA RAG
## 🛠️ Technology Stack
| Component | Choice | Why |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Ecosystem standard for data pipelines and machine learning. |
| **PDF Extraction** | PyMuPDF (fitz) | High-speed, granular extraction perfect for attaching 1-indexed page numbers. |
| **Chunking** | LangChain Text Splitters | `RecursiveCharacterTextSplitter` preserves semantic blocks and paragraph structures. |
| **Embeddings** | HuggingFace (BGE-Small) | Lightweight, highly accurate local open-source embeddings. |
| **Vector DB** | ChromaDB | Developer-friendly local persistence engine optimized for metadata filtering. |
| **Retriever** | EnsembleRetriever | Combines 50% dense vector search (semantic) with 50% BM25 (sparse keyword). |
| **LLM Engine** | Gemini 1.5 Flash | Ultra-low latency, 100% free tier, and exceptional at following strict guardrails. |
| **Frontend UI** | Streamlit | Rapid prototyping for data applications. |
## 🏁 Quickstart

### Prerequisites

- Python 3.10 or higher
- Git

### 1. Install

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/vaishnaviomkaram/Internship-1
pip install -r requirements.txt
```

### 2. Run Local Data Ingestion (Week 1 & 2 Pipeline)

Place a sample PDF in the `data/` folder (e.g., `sample_textbook.pdf`), then execute the ingestion script to parse, chunk, and embed the document:

```bash
python src/ingestion.py
```

### 3. Test the Retrieval Pipeline

> **Note:** The frontend UI is currently under development. To test the core extraction logic:

```bash
python src/ingestion.py
python src/rag_pipeline.py
```

---

## 📁 Data Sources

The primary data corpus consists of local PDF documents (e.g., academic textbooks, research papers) placed into the `data/` directory. The system does not rely on external internet searches, keeping the generation boundary strictly confined to the uploaded documents.

---


## 📜 Architecture Decision Records (ADRs)

- **ADR-001:** Vector Database Selection — *Drafting*
- **ADR-002:** Retrieval Engine Design — *Drafting*
- **ADR-003:** LLM Engine Selection — *Drafting*

---

## 🚀 Upcoming: The Mini-Extension (Week 3)

### Compare Two Documents

The system will be upgraded to support multi-document reasoning. Users will be able to upload two distinct PDFs (e.g., two research papers) and query the system to retrieve, compare, and contrast information across both sources simultaneously.

---

## ⚠️ Known Limitations

- Currently optimized for text-heavy PDFs; complex tables or image-based scans (requiring OCR) may lose formatting fidelity during extraction.
- The local embedding model (BGE-Small) is highly efficient but may require hyperparameter tuning for highly specialized medical or legal corpora.

---

## 🔮 What I'd Do in 3rd Year

This foundational project is designed to scale into the 3rd-year **E3 (Enterprise Unstructured Data RAG)** problem statement.

> **View the full roadmap here:** in docs/*3rd Year Roadmap (Coming Soon)*

---

## 📄 License & Acknowledgements

Built as part of the **2nd Year B.Tech CSE-AIDE Internship Program (2026).**
````
