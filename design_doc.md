# Design Document

## Project: AI-Powered Document Question Answering System (RAG)

**Author:** Vaishnavi  
**Project Type:** Applied Machine Learning  
**Domain:** Natural Language Processing (NLP) & Large Language Models (LLMs)

---

# Table of Contents

1. Introduction
2. Problem Statement
3. Objectives
4. System Overview
5. Architecture
6. Technology Stack
7. Functional Requirements
8. Non-Functional Requirements
9. Workflow
10. System Modules
11. Data Flow
12. Folder Structure
13. Testing Strategy
14. Future Improvements
15. Conclusion

---

# 1. Introduction

The **AI-Powered Document Question Answering System** is an intelligent application that enables users to ask questions about uploaded documents using natural language.

Instead of manually searching through lengthy PDFs, the system uses **Retrieval-Augmented Generation (RAG)** to retrieve the most relevant information from uploaded documents and generates accurate responses using a Large Language Model (LLM).

---

# 2. Problem Statement

Searching through academic books, research papers, regulations, reports, and other lengthy documents is often inefficient and time-consuming.

Traditional keyword search cannot understand context or semantics, making it difficult to locate precise information.

This project creates an intelligent assistant capable of understanding user queries, retrieving relevant document sections, and generating context-aware answers.

---

# 3. Objectives

## Primary Objectives

- Upload and process PDF documents
- Extract and clean document text
- Generate semantic embeddings
- Store embeddings in a vector database
- Retrieve relevant information efficiently
- Generate accurate answers using retrieved context

## Secondary Objectives

- Modular architecture
- User-friendly interface
- Source attribution
- Future scalability

---

# 4. System Overview

The system consists of six stages:

1. Document Upload
2. Text Extraction
3. Text Chunking
4. Embedding Generation
5. Semantic Retrieval
6. Answer Generation

---

# 5. Architecture

```text
                    User
                      │
                      ▼
             Streamlit Interface
                      │
                      ▼
             PDF Document Upload
                      │
                      ▼
             Text Extraction Layer
                      │
                      ▼
             Text Chunking Module
                      │
                      ▼
            Embedding Generation
                      │
                      ▼
            FAISS Vector Database
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
   User Question            Query Embedding
         └────────────┬────────────┘
                      ▼
             Similarity Search
                      ▼
          Retrieve Relevant Chunks
                      ▼
          Prompt Construction Layer
                      ▼
          Large Language Model (LLM)
                      ▼
               Generated Response
```

---

# 6. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Frontend | Streamlit |
| Framework | LangChain |
| Embeddings | Google Gemini / OpenAI |
| Vector Database | FAISS |
| PDF Loader | PyPDFLoader |
| Version Control | Git & GitHub |

---

# 7. Functional Requirements

- Upload one or more PDF documents
- Extract text
- Split text into overlapping chunks
- Generate embeddings
- Store vectors in FAISS
- Perform semantic similarity search
- Generate grounded responses
- Display source passages

---

# 8. Non-Functional Requirements

- Fast retrieval
- Reliable processing
- Modular codebase
- Scalable architecture

---

# 9. Workflow

1. Upload PDF documents.
2. Extract document text.
3. Split text into overlapping chunks.
4. Generate embeddings for every chunk.
5. Store embeddings in FAISS.
6. Convert the user query into an embedding.
7. Retrieve the most relevant chunks.
8. Build a prompt using the retrieved context.
9. Generate the final answer using the LLM.

---

# 10. System Modules

- `document_loader.py`
- `text_splitter.py`
- `embeddings.py`
- `vector_store.py`
- `retriever.py`
- `rag_pipeline.py`
- `app.py`

---

# 11. Data Flow

```text
PDF Upload
    ↓
Text Extraction
    ↓
Chunking
    ↓
Embeddings
    ↓
FAISS
    ↓
User Query
    ↓
Query Embedding
    ↓
Similarity Search
    ↓
Relevant Chunks
    ↓
LLM
    ↓
Answer
```

---

# 12. Folder Structure

```text
Document-QA-RAG/
├── app.py
├── README.md
├── design_doc.md
├── requirements.txt
├── src/
├── data/
├── vectorstore/
└── assets/
```

---

# 13. Testing Strategy

- Unit testing
- Integration testing
- End-to-end workflow validation
- User acceptance testing

---

# 14. Future Improvements

- OCR support
- Multi-document comparison
- Conversation memory
- Hybrid search
- Cloud deployment
- Authentication

---

# 15. Conclusion

This project demonstrates a complete Retrieval-Augmented Generation (RAG) pipeline, combining semantic search, vector databases, and Large Language Models to provide accurate, context-aware answers from uploaded documents. The modular architecture is designed for maintainability, scalability, and future enhancements.
