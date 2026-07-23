# Evaluation Report — AskMyBook

**Project:** AskMyBook  
**Problem Code:** I2 — Document Q&A  
**Author:** Vaishnavi  
**Evaluation Method:** Manual + LLM-as-Judge using Eval mode  
**Scoring Scale:** 1 to 5 for each axis  

---

## Evaluation Axes

| Axis | Meaning |
|---|---|
| Correctness | Is the answer factually grounded in the retrieved context? If outside knowledge appears, score should be low. |
| Citation Precision | Are page citations present, accurate, and correctly formatted? |
| Completeness | Does the answer fully address the question using available context? |

---

## Test Document

| Field | Value |
|---|---|
| Document used | TODO: name of PDF used |
| Document type | TODO: textbook / research paper / handbook / notes |
| Number of pages | TODO |
| Vector store reset before testing? | Yes / No |
| Retrieval k | TODO, default 4 or 6 |

---

## Scoring Summary

| Metric | Average Score |
|---|---:|
| Correctness | TODO / 5 |
| Citation Precision | TODO / 5 |
| Completeness | TODO / 5 |
| Overall Average | TODO / 5 |

---

## 24 Test Questions

Replace bracketed topics with actual topics from your test PDF.

| # | Question | Correctness | Citation | Completeness | Notes |
|---|---|---:|---:|---:|---|
| 1 | What is the main subject of this document? | TODO | TODO | TODO |  |
| 2 | Summarize the first section or chapter. | TODO | TODO | TODO |  |
| 3 | Define [important term from document]. | TODO | TODO | TODO |  |
| 4 | Explain [core concept from document] in simple words. | TODO | TODO | TODO |  |
| 5 | What are the key differences between [concept A] and [concept B]? | TODO | TODO | TODO |  |
| 6 | List the main steps involved in [process from document]. | TODO | TODO | TODO |  |
| 7 | What does the document say about [specific topic]? | TODO | TODO | TODO |  |
| 8 | Give an example of [concept] from the document. | TODO | TODO | TODO |  |
| 9 | What is the purpose of [component/method/theory]? | TODO | TODO | TODO |  |
| 10 | Explain the relationship between [A] and [B]. | TODO | TODO | TODO |  |
| 11 | What are the advantages of [topic] mentioned in the document? | TODO | TODO | TODO |  |
| 12 | What are the limitations or disadvantages of [topic]? | TODO | TODO | TODO |  |
| 13 | What is the meaning of [formula/equation/definition]? | TODO | TODO | TODO |  |
| 14 | Which page discusses [topic]? | TODO | TODO | TODO | Citation test |
| 15 | Quote the document’s definition of [term]. | TODO | TODO | TODO | Citation test |
| 16 | What did the author conclude about [topic]? | TODO | TODO | TODO |  |
| 17 | Compare [section A] and [section B]. | TODO | TODO | TODO |  |
| 18 | What would happen if [condition from document]? | TODO | TODO | TODO |  |
| 19 | Why is [concept] important according to the document? | TODO | TODO | TODO |  |
| 20 | What are the prerequisites for understanding [topic]? | TODO | TODO | TODO |  |
| 21 | What is not mentioned in the document: [plausible but absent topic]? | TODO | TODO | TODO | Guardrail test |
| 22 | What is the capital of France? | TODO | TODO | TODO | Out-of-corpus test; should refuse |
| 23 | Write Python code to sort a list. | TODO | TODO | TODO | Guardrail test; should refuse if not in document |
| 24 | Summarize the document in three bullet points with citations. | TODO | TODO | TODO |  |

---

## Observations

### What worked well

- TODO: Example: citations were accurate for direct definition questions.
- TODO: Example: hybrid retrieval helped exact-term questions.
- TODO: Example: guardrails worked for out-of-corpus questions.

### What failed or needs improvement

- TODO: Example: long answers sometimes missed one citation.
- TODO: Example: table-heavy pages produced weaker extraction.
- TODO: Example: some answers were too brief for multi-part questions.

---

## Conclusion

TODO: Write 3–5 sentences summarizing overall quality.

Example structure:

> The system performed best on factual, document-grounded questions where the relevant section was retrieved correctly. Citation precision was strong for direct definitions but weaker for longer synthesized answers. Guardrails worked well for out-of-corpus questions. The main improvement areas are table extraction, multi-part question completeness, and automated batch evaluation.
