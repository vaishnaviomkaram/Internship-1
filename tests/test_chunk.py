import pytest
from src.chunk import DocumentChunker

class TestDocumentChunker:
    """Test suite for the semantic structural chunking logic."""

    def test_chunk_pages_creates_valid_chunks(self):
        # 1. Setup: Initialize chunker with artificially small limits to force a split
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        
        # Create mock input mirroring the output of ingest.py
        raw_pages = [
            {
                "text": "This is a very long sentence that needs to be split into smaller pieces for testing.",
                "metadata": {"source": "textbook.pdf", "page": 1}
            }
        ]
        
        # 2. Execute: Run the chunker
        chunks = chunker.chunk_pages(raw_pages)
        
        # 3. Assert: Validate the output
        assert len(chunks) > 1, "The text should have been split into multiple chunks."
        assert isinstance(chunks, list), "Output must be a list."
        
        for chunk in chunks:
            # Check structure
            assert "text" in chunk, "Each chunk must have a 'text' key."
            assert "metadata" in chunk, "Each chunk must have a 'metadata' key."
            
            # Check metadata preservation
            assert chunk["metadata"]["source"] == "textbook.pdf", "Source metadata must be preserved."
            assert chunk["metadata"]["page"] == 1, "Page metadata must be preserved."
            
            # Check length constraint
            assert len(chunk["text"]) <= 50, f"Chunk size exceeded limit: {len(chunk['text'])} > 50"

    def test_empty_pages_handled_gracefully(self):
        # 1. Setup
        chunker = DocumentChunker()
        raw_pages = []
        
        # 2. Execute
        chunks = chunker.chunk_pages(raw_pages)
        
        # 3. Assert
        assert chunks == [], "Empty input should return an empty list."