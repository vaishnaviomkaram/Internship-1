import os
import fitz  # PyMuPDF
from typing import List, Dict, Any

class DocumentIngestor:
    """Handles raw PDF parsing, extracting text and page metadata."""
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        
        raw_pages = []
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text("text")
            if text.strip():
                raw_pages.append({
                    "text": text,
                    "metadata": {
                        "source": os.path.basename(file_path), 
                        "page": page_num + 1
                    }
                })
        doc.close()
        return raw_pages