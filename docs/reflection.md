# Reflection — AskMyBook: AI-Powered Document Q&A System

**Name:** Vaishnavi  
**Segment:** Foundations of Applied Machine Learning  
**Problem Code:** I2 — Document Q&A: RAG over a Focused Corpus  
**Duration:** 22 June 2026 — 26 July 2026  

---

## Section 1: What I Built

AskMyBook is a document question-answering system built using Retrieval-Augmented Generation, commonly called RAG. The product allows a user to upload a PDF document, such as a textbook, research paper, handbook, or set of course notes, and then ask natural-language questions about it. Instead of sending the entire document directly to a large language model, the system extracts text from the PDF, splits it into meaningful chunks, converts those chunks into embeddings, stores them in a local vector database, and retrieves only the most relevant chunks when the user asks a question.

The retrieved chunks are passed to the LLM along with strict guardrails. The model is instructed to answer only from the provided context, include inline page citations, and say “I don’t know based on the provided document” if the answer cannot be constructed from the retrieved evidence. This reduces hallucination and makes the system more trustworthy for academic use.

The mini-extension I built is the **Compare Two Documents** mode. This allows a user to upload two separate PDFs and ask comparative questions such as “How do these two documents explain topic X differently?” The system retrieves relevant chunks from both documents independently and uses a specialized comparator prompt to analyze them side by side. I chose this extension because single-document RAG is now a common starter project, but multi-document reasoning is more challenging and closer to real-world use cases such as comparing syllabus versions, research papers, policy documents, or textbook editions.

---

## Section 2: What I Learned About the Tools

### PyMuPDF

PyMuPDF, imported as `fitz`, was used for PDF text extraction. Before this project, I thought PDF parsing would be simple: just “read the file as text.” I quickly learned that PDFs are not clean text files. They are layout-based documents, and extraction can produce blank pages, odd spacing, and broken structure.

What surprised me was how important metadata is. If page numbers are not attached during extraction, citations become unreliable later. By tagging each extracted page with its source filename and 1-indexed page number early, every downstream chunk inherited correct citation metadata.

If a friend were about to learn PyMuPDF, I would tell them: do not treat ingestion as a boring preprocessing step. In RAG, ingestion quality directly decides answer quality.

### LangChain Text Splitters

I used LangChain’s `RecursiveCharacterTextSplitter` to chunk extracted text. Earlier, I thought chunking meant cutting text into fixed-size pieces. This project taught me that good chunking should respect semantic boundaries such as paragraphs, sentences, and natural separators.

The recursive splitter tries larger structural separators first and then falls back to smaller ones. This reduces the chance of breaking a concept in the middle. I also learned that chunk overlap is useful because it helps preserve context between adjacent chunks.

If I were explaining this to a friend, I would say: chunking is not just a size problem; it is a context-preservation problem.

### Chroma

Chroma was used as the local vector database. I chose it because it is simple, developer-friendly, and supports local persistence. This mattered because I wanted the app to avoid re-embedding the same document repeatedly.

What surprised me was how much vector storage changes the feel of an application. Once the document is embedded and stored, retrieval becomes fast and the app feels more responsive. I also learned that metadata filtering and clean persistence directories are important when managing multiple documents or modes.

I would tell a friend: Chroma is easy to start with, but you must still think carefully about where vector stores are saved, how they are reset, and how duplicate chunks are avoided.

### HuggingFace Embeddings

I used the `BAAI/bge-small-en-v1.5` embedding model locally. This was an important decision because it avoided API costs and rate limits for embeddings. Embeddings are called often during indexing and retrieval, so keeping them local made the system more practical.

What surprised me was that a small local embedding model could be good enough for this project. I did not need a huge model to get useful semantic search. I also learned the difference between dense semantic search and sparse keyword search. Dense search is good for meaning, but it can miss exact terms. That realization led to the hybrid retrieval design.

If a friend were learning embeddings, I would say: do not start by asking which model is biggest. Start by asking which model is good enough for your retrieval task and deployment constraints.

### Gemini API

Gemini was used for generation, quiz creation, comparison, and evaluation. I kept embeddings local but used Gemini for language generation because generation quality and instruction-following matter a lot for the final user experience.

What surprised me was how much prompt engineering matters. The model is capable, but it still needs strict instructions. I had to repeatedly enforce rules such as “use only the context,” “include citations,” “do not generate code,” and “return JSON only.” Even then, the model sometimes wrapped JSON in markdown backticks, so I added cleanup logic.

I would tell a friend: using an LLM API is not just calling a function. You are designing a contract between your application and the model.

### Streamlit

Streamlit was used for the frontend. It allowed me to build the UI quickly, but it also taught me a hard lesson about state management. Streamlit reruns the script on every interaction, so variables do not persist unless you explicitly store them in session state.

This became obvious when I faced bugs where chat history or document paths leaked across modes. That led to the isolated workspace design described in ADR-003. Each mode now has its own state namespace.

If a friend were learning Streamlit, I would say: it is easy to prototype with, but you must understand session state early, otherwise your app will behave unpredictably.

---

## Section 3: What I Learned About Myself

This project taught me that I enjoy building systems where multiple components connect into a working product. I especially enjoyed designing the retrieval and prompting layers. There was something satisfying about taking a messy PDF, cleaning it, chunking it, embedding it, retrieving relevant pieces, and then forcing the LLM to answer responsibly.

The hardest part was not one single technology. It was managing complexity across many small pieces. A bug in ingestion could appear as a bad answer. A bad prompt could look like a retrieval problem. A Streamlit state issue could look like a model issue. Debugging required patience and a methodical approach.

I also learned that I underestimated documentation. At first, I wanted to focus only on making the app work. But writing ADRs, updating the README, and explaining decisions forced me to understand my own system better. Documentation was not just a deliverable; it was a thinking tool.

Some work was harder than expected. Deployment was harder than I expected because local assumptions broke in the cloud. Environment variables, file paths, and permissions all mattered. Testing was also harder than expected because I had to mock external dependencies instead of relying on real PDFs or API calls.

Some work was easier than expected. Once the basic RAG pipeline worked, adding new modes became easier because the core modules were separated. Modularization paid off.

I also had to be honest about my schedule. There were days when I lost momentum, and during Week 3 I was ill, which made the Milestone 1 push harder. I learned that hiding delays makes things worse. The best response was to scope work carefully, communicate, and keep moving in small steps.

I enjoyed debugging more than I expected when the bug was clear and reproducible. I disliked debugging when the failure was vague, especially when the LLM output changed between runs. That taught me the importance of deterministic settings, guardrails, and evaluation.

---

## Section 4: What I Would Do Differently

If I started over, I would create the evaluation plan earlier. I spent a lot of time building features before I had a structured way to judge whether the answers were actually good. If I had prepared 20 test questions in Week 1 or Week 2, I could have measured improvement more objectively.

I would also write tests earlier. I initially treated tests as something to add near the end, but tests would have helped me catch ingestion and chunking issues faster. Mocking external dependencies felt difficult at first, but it made the project more reliable.

I would also design the Streamlit session state more carefully from the beginning. The cross-mode leakage bug happened because I did not fully understand how Streamlit reruns the script. If I had planned isolated state namespaces earlier, I would have avoided debugging time.

I wish my mentor had told me on Day 1: “Your RAG system is only as good as your weakest prompt and your messiest PDF.” I thought retrieval and embeddings would be the main challenge. In reality, guardrails, citation formatting, JSON parsing, and document messiness took a lot of effort.

I would also spend more time on deployment earlier. Waiting until later to deploy made me discover environment issues late. A simple early deployment, even with a basic UI, would have reduced risk.

---

## Section 5: What’s Next — The 3rd Year Plan

This project is the foundation for a much larger 3rd-year portfolio piece. Right now, AskMyBook works well for clean, text-based PDFs in a single-user setting. In 3rd year, I want to extend it toward enterprise-style document intelligence.

The first extension will be OCR support so that scanned documents and image-based PDFs can be processed. The second extension will be multi-format ingestion, including DOCX, Markdown, and possibly web pages. The third extension will be persistent user sessions and document libraries, so users do not lose their work when the browser refreshes.

After that, I want to build a stronger evaluation pipeline. Instead of manually testing questions, I want a batch evaluation script that can run many questions, score answers, and produce a report automatically. This will make the project more production-ready.

By the time of my 3rd-year internship, I want this project to become a multi-source RAG system that can handle messy, heterogeneous document collections. That maps naturally to the 3rd-year Applied ML extension path, especially enterprise RAG and document intelligence problem statements.

This internship taught me that a good project is not just code. It is a working system, clear documentation, honest evaluation, and a plan for what comes next.
