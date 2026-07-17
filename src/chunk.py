from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

class DocumentChunker:
    """Handles semantic and structural chunking to preserve context."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_pages(self, raw_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for page in raw_pages:
            page_chunks = self.text_splitter.split_text(page["text"])
            for chunk_text in page_chunks:
                chunks.append({
                    "text": chunk_text,
                    "metadata": page["metadata"].copy()
                })
        return chunks