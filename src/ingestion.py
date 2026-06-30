import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # We use RecursiveCharacterTextSplitter for structural chunking.
        # It splits by paragraphs (\n\n), then sentences (\n), then words, 
        # ensuring semantic blocks stay together as much as possible.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def load_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Loads a PDF using PyMuPDF and extracts text page by page.
        Crucial: We attach the page number to the metadata for citations later.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        raw_pages = []
        try:
            # Open the PDF with PyMuPDF
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                
                # Only keep pages that actually have text
                if text.strip():
                    raw_pages.append({
                        "page_content": text,
                        "metadata": {
                            "source": os.path.basename(file_path),
                            "page": page_num + 1 # 1-indexed for human readability
                        }
                    })
            doc.close()
            print(f"Successfully loaded {len(raw_pages)} pages from {file_path}")
            return raw_pages
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []

    def chunk_documents(self, raw_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw page dictionaries and chunks them while preserving metadata.
        """
        chunks = []
        for page in raw_pages:
            # Split the text of a single page into smaller chunks
            page_chunks = self.text_splitter.split_text(page["page_content"])
            
            for chunk_text in page_chunks:
                chunks.append({
                    "page_content": chunk_text,
                    "metadata": page["metadata"].copy()
                })
                
        print(f"Split {len(raw_pages)} pages into {len(chunks)} semantic chunks.")
        return chunks







# Quick Test Block (Runs only if you execute this file directly)

if __name__ == "__main__":
    # 1. Creating a dummy PDF path (will replace this with a real PDF in our data/ folder)
    test_pdf_path = "../data/sample_textbook.pdf" 
    
    # 2. Initialize processor
    processor = DocumentProcessor(chunk_size=800, chunk_overlap=150)
    
    # 3. Test if the file exists and process it
    if os.path.exists(test_pdf_path):
        print("Starting ingestion test...")
        pages = processor.load_pdf(test_pdf_path)
        final_chunks = processor.chunk_documents(pages)
        
        # Printing a sample chunk to verify metadata is intact
        if final_chunks:
            print("\n--- SAMPLE CHUNK ---")
            print(f"Metadata: {final_chunks[0]['metadata']}")
            print(f"Content: {final_chunks[0]['page_content']}...") # Printing the first chunk
    else:
        print(f"⚠️ Please place a test PDF at '{test_pdf_path}' to run this test locally.")
