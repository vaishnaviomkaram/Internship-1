import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def load_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts text page by page, keeping page numbers in metadata."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        raw_pages = []
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text("text")
            if text.strip():
                raw_pages.append({
                    "page_content": text,
                    "metadata": {"source": os.path.basename(file_path), "page": page_num + 1}
                })
        doc.close()
        return raw_pages

    def chunk_documents(self, raw_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits pages into smaller semantic chunks."""
        chunks = []
        for page in raw_pages:
            page_chunks = self.text_splitter.split_text(page["page_content"])
            for chunk_text in page_chunks:
                chunks.append({
                    "page_content": chunk_text,
                    "metadata": page["metadata"].copy()
                })
        return chunks