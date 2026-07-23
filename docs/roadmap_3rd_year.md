# AskMyBook — 3rd Year Extension Roadmap

## What this project is today

AskMyBook is a text-based PDF document Q&A system using RAG. It supports chat, two-document comparison, quiz generation, and LLM-as-Judge evaluation. It uses local embeddings, Chroma vector storage, hybrid BM25 + dense retrieval, and Gemini-based guarded generation.

## The arc: where this could be by 3rd year internship (May 2027)

By May 2027, this project should grow from a single-user PDF Q&A demo into a multi-source document intelligence platform. It should support scanned documents, multiple file formats, persistent user workspaces, automated evaluation, and more advanced query handling. The goal is not just to answer questions, but to reliably reason over messy real-world document collections with traceable citations and measurable quality.

---

## 3rd Year Semester Plan (Aug 2026 - Dec 2026)

### Milestone 1 (Aug-Sep 2026): Robust Ingestion and OCR

**What I’ll add:**

- OCR support for scanned PDFs using Tesseract or a cloud OCR service
- Multi-format ingestion: PDF, DOCX, Markdown, TXT
- Better extraction quality for headings, tables, and section structure
- Document health report: number of pages extracted, empty pages skipped, OCR confidence

**Tools I’ll learn:**

- Tesseract OCR
- pytesseract
- Unstructured.io or LlamaParse
- Basic table extraction
- File-type detection and encoding handling

**Time commitment:**

- 6–8 hours/week

**Done looks like:**

- A scanned PDF can be uploaded and answered from
- Extraction quality is visible in the UI
- The system does not silently fail on bad documents

---

### Milestone 2 (Oct-Nov 2026): Persistence and User Workspaces

**What I’ll add:**

- User accounts or lightweight workspace IDs
- Persistent document libraries
- Saved chat history
- Stored vector store metadata
- Reset/delete document options

**Tools I’ll learn:**

- SQLite or Postgres
- Basic authentication
- Streamlit session persistence patterns
- File storage organization
- Background processing for large uploads

**Time commitment:**

- 6–8 hours/week

**Done looks like:**

- A user can upload a document, close the browser, return later, and continue chatting
- Vector stores are not lost on refresh
- Each user/workspace has isolated documents

---

### Milestone 3 (Nov-Dec 2026): Automated Evaluation and Observability

**What I’ll add:**

- Batch evaluation script for 50+ questions
- Golden answer dataset
- Automated scoring for correctness, citation precision, completeness
- Retrieval quality metrics: recall@k, precision@k, MRR
- Logging dashboard for failures and low-score answers

**Tools I’ll learn:**

- Ragas or DeepEval
- pytest for evaluation regression
- Logging and tracing
- Basic metrics visualization
- Prompt versioning

**Time commitment:**

- 7–9 hours/week

**Done looks like:**

- One command runs the full evaluation suite
- Each prompt/model change produces a comparable score report
- Low-quality answers can be inspected and debugged

---

## 3rd Year Internship Plan (Jun-Jul 2027)

By 3rd-year internship, this project can become an **Enterprise Document Intelligence RAG System**.

It can target the 3rd-year Applied ML problem statement around enterprise RAG over messy, heterogeneous sources. The system would handle multiple document types, dirty layouts, access control, evaluation, and possibly agentic query decomposition.

Possible 3rd-year internship framing:

> Build a production-grade RAG system that answers questions across heterogeneous enterprise documents with citation traceability, evaluation metrics, and guardrails against hallucination.

---

## What I’ll need from the placement / mentor ecosystem

- Mentor feedback on evaluation design
- Example enterprise document datasets or synthetic messy documents
- Guidance on production RAG patterns
- Exposure to vector databases at larger scale
- Feedback on system design and deployment
- Mock interviews focused on RAG, retrieval, and LLM evaluation

---

## Risks & open questions

| Risk | Why it matters | Mitigation |
|---|---|---|
| OCR quality may be poor | Bad extraction leads to bad answers | Add OCR confidence scores and fallback warnings |
| Evaluation is subjective | Hard to prove improvement | Build golden dataset and automated metrics |
| Scope creep | Too many features, weak core | Ship one milestone at a time |
| API cost and rate limits | Heavy evaluation may exceed free tier | Use local embeddings, cache generations, sample eval sets |
| Deployment complexity | More features increase infra burden | Start with simple persistence before moving to full backend |
