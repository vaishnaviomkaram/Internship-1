import pytest
from unittest.mock import patch, MagicMock
from src.ingest import DocumentIngestor

class TestDocumentIngestor:
    """Test suite for PDF ingestion and metadata extraction."""

    def test_file_not_found_raises_error(self):
        # 1. Execute & Assert
        # Checks that the specific FileNotFoundError is raised for a bad path
        with pytest.raises(FileNotFoundError, match="not found"):
            DocumentIngestor.parse_pdf("this_file_does_not_exist.pdf")

    @patch("src.ingest.os.path.exists")
    @patch("src.ingest.fitz.open")
    def test_successful_pdf_parsing_with_mock(self, mock_fitz_open, mock_exists):
        # 1. Setup: Fake the file system and PDF reader
        mock_exists.return_value = True
        
        # Create a fake PDF page with sample text
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is fake text from page 1."
        
        # Create a fake PDF document that contains our fake page
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1  # Simulate a 1-page document
        mock_doc.load_page.return_value = mock_page
        
        # Tell fitz.open to return our fake document
        mock_fitz_open.return_value = mock_doc
        
        # 2. Execute
        raw_pages = DocumentIngestor.parse_pdf("mocked_document.pdf")
        
        # 3. Assert
        assert len(raw_pages) == 1, "Should return exactly one page."
        
        page_data = raw_pages[0]
        assert page_data["text"] == "This is fake text from page 1.", "Text extraction failed."
        
        # Verify metadata dictionary structure
        assert page_data["metadata"]["page"] == 1, "Page number should be 1-indexed."
        assert page_data["metadata"]["source"] == "mocked_document.pdf", "Source filename should match."
        
        # Verify that the PDF document was properly closed after processing
        mock_doc.close.assert_called_once()
