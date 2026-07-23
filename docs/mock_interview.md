# Mock Interview — 5 Questions and Answers

## Question 1: What is RAG, and why did you use it instead of fine-tuning?

RAG stands for Retrieval-Augmented Generation. Instead of relying only on the LLM’s internal knowledge, RAG retrieves relevant pieces from a source document and passes them to the model as context. The model then answers based on that retrieved evidence.

I used RAG because the goal was document-specific question answering. Fine-tuning would be expensive, slower to update, and less transparent. If the textbook changes, RAG only requires re-indexing the document. RAG also allows citations, which makes answers more trustworthy.

---

## Question 2: Why did you use hybrid retrieval instead of only dense vector search?

Dense vector search is good at semantic similarity. It can find answers even when the user’s wording is different from the document. However, it can miss exact terms, names, formulas, or specific phrases.

BM25 is good at exact keyword matching. By combining BM25 and dense retrieval in a 50/50 ensemble, the system handles both conceptual questions and precise lookup questions better. For example, dense search helps with “explain the main idea,” while BM25 helps with “find the definition of X” or “what is equation 4.2?”

---

## Question 3: How did you reduce hallucination?

I used several layers of guardrails.

First, the system retrieves only relevant document chunks. Second, the prompt tells the model to use only the provided context. Third, the model is instructed to say “I don’t know based on the provided document” if the answer cannot be constructed. Fourth, answers must include inline page citations. Fifth, the evaluation prompt penalizes outside knowledge heavily.

No system can eliminate hallucination completely, but these steps make it less likely and easier to detect.

---

## Question 4: How did you handle citations?

During PDF extraction, I attached page metadata to each page using PyMuPDF. When the text was chunked, each chunk inherited its parent page number. During retrieval, the page number remained available in the chunk metadata.

The generation prompt then required the model to cite quoted text with page numbers, for example: `"quoted text" (Page 5)`. This makes the answer traceable back to the source document.

---

## Question 5: If this system were used by thousands of users, what would you change?

For many users, I would move from a single-user Streamlit app to a proper backend architecture.

I would add:

- User authentication
- Persistent document storage
- A managed vector database
- Background jobs for ingestion
- Caching for frequent queries
- Rate limiting and API key management
- Automated evaluation and monitoring
- Logging and tracing for retrieval and generation

I would also consider OCR, multi-format ingestion, and access control if users uploaded sensitive documents.
