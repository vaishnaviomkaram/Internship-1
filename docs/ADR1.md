# ADR-001: Offloading LLM Generation to External APIs vs. Local Models

## 1. Context

Our application requires a robust Large Language Model 
(LLM) to synthesize answers based on retrieved document chunks (RAG) and
 generate strictly formatted JSON quizzes. Initially, the plan could 
have involved running a local model to ensure complete data privacy and 
offline capability. However, local LLMs require significant disk space, 
high VRAM, and heavy computational resources which slow down the rapid 
prototyping phase and strain local hardware.

**Resource Constraints Analysis:**

| Resource Requirement | Local LLM (e.g., 7B-8B parameters) | External API (Gemini Flash Lite) | Impact on MVP Development |
| --- | --- | --- | --- |
| **Disk Space** | ~4GB to 15GB+ per model | **0 MB** (Cloud Hosted) | Local storage fills up quickly during iteration. |
| **VRAM / RAM** | 8GB - 16GB minimum | **Minimal** (Standard HTTP requests) | Local hardware stutters; background processes crash. |
| **Processing Speed** | Slow (Tokens generated locally) | **Ultra-fast** (Cloud inference) | UI feels sluggish locally, breaking the UX. |
| **JSON Adherence** | Inconsistent on smaller models | **Highly reliable** | Breaking JSON formats crashes the quiz generator. |

## 2. Decision

We chose to implement a **Hybrid Inference Architecture**.

1. **Local Embeddings:** We keep the vector embeddings local using `BAAI/bge-small-en-v1.5`.


2. **External LLM Generation:** We offload the heavy lifting to Google's Generative AI (`gemini-3.1-flash-lite`) via `langchain-google-genai` for all text synthesis and quiz generation tasks within the RAG pipeline.



### Architecture Flow Diagram

```text
┌────────────────────┐      ┌─────────────────────────┐
│  User Input (PDF)  │ ───▶│ PyMuPDF & Text Splitter  │
└────────────────────┘      └────────────┬────────────┘
                                         │
 ┌───────────────────────────────────────▼─────────────────────────────────────┐
 │ LOCAL ENVIRONMENT                                                           │
 │                                                                             │
 │  ┌────────────────────────┐      ┌────────────┐      ┌───────────────────┐  │
 │  │ HuggingFace Embeddings │ ───▶│  ChromaDB   │ ───▶│ Hybrid Retriever  │  │
 │  │ (BAAI/bge-small)       │      │  (Vectors) │      │ (BM25 + Semantic) │  │
 │  └────────────────────────┘      └────────────┘      └─────────┬─────────┘  │
 └────────────────────────────────────────────────────────────────┼────────────┘
                                                                  │
 ┌────────────────────────────────────────────────────────────────▼────────────┐
 │ EXTERNAL CLOUD (Google API)                                                 │
 │                                                                             │
 │  ┌───────────────────────────────────────────────────────────────────────┐  │
 │  │ ChatGoogleGenerativeAI (gemini-3.1-flash-lite)                        │  │
 │  │ Parses retrieved context + chat history -> Generates JSON / Text      │  │
 │  └───────────────────────────────────────────────────────────────────────┘  │
 └────────────────────────────────────────────────┬────────────────────────────┘
                                                  │
┌────────────────────┐      ┌─────────────────────▼───────────────────┐
│ Streamlit Frontend │ ◀───│ Final Output (Chat Answer / JSON Quiz)   │
└────────────────────┘      └─────────────────────────────────────────┘

```

## 3. Consequences

### Positive Impacts (The "Why")

* **Rapid UI Responsiveness:** By offloading inference, the Streamlit application remains highly responsive and answers stream in rapidly.
* **Massive Storage & Compute Savings:** Bypassing local 10GB+ model downloads saves local disk space and prevents VRAM exhaustion.


* **Strict Format Adherence:** The Gemini engine strictly follows prompt instructions (e.g., returning clean JSON arrays for the mini-extension) much better than smaller local, open-weights models.



### Negative Trade-offs (The Risks)

* **Internet Dependency:** The RAG pipeline will instantly fail if the host machine loses internet access or if the external API experiences downtime.
* **Strict Credit Quotas:** We are heavily constrained by the daily free-tier credit quota provided by the API. High-volume testing and debugging sessions might be throttled, causing `429 Too Many Requests` errors.
* **Privacy Concerns:** Uploaded document context is sent to external servers, meaning highly sensitive or classified textbook PDFs cannot be used in the current pipeline without reviewing Google's API data retention policies.

## 4. Alternatives Considered

| Alternative Solution | Description | Reason for Rejection |
| --- | --- | --- |
| **Fully Local LLMs (Ollama / Llama.cpp)** | Running models like Llama 3 (8B) or Gemma (2B) locally on the machine. | **Rejected:** Running them locally causes heavy system latency on standard laptops. Deploying them requires expensive cloud GPUs, which defeats the "skinny MVP" constraint.|
| **Different External API (OpenAI / Anthropic)** | Using `gpt-4o-mini` or `Claude 3 Haiku`. | **Rejected:** While highly capable, setting up billing accounts for prototyping was unnecessary when a highly performant free tier was available for the Google GenAI suite. |
| **Local Small Language Models (SLMs)** | Running ultra-tiny models (< 1B parameters) locally for text generation. | **Rejected:** SLMs struggled heavily with the strict JSON formatting required by the Quiz Generation module, returning markdown wrappers or malformed arrays that broke the UI logic.|





