import os
import pytest
from resume_iq.ingestion.loaders import DocumentLoaderFactory, PDFLoader, DOCXLoader
from resume_iq.ingestion.exceptions import (
    UnsupportedFileTypeError,
    EmptyDocumentError,
    FileSizeExceededError
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fixtures_dir = os.path.join(base_dir, "fixtures")

def test_factory_dispatch():
    pdf_path = os.path.join(fixtures_dir, "single_page.pdf")
    docx_path = os.path.join(fixtures_dir, "normal.docx")
    
    if os.path.exists(pdf_path):
        pdf_loader = DocumentLoaderFactory.get_loader(pdf_path)
        assert isinstance(pdf_loader, PDFLoader)
    
    if os.path.exists(docx_path):
        docx_loader = DocumentLoaderFactory.get_loader(docx_path)
        assert isinstance(docx_loader, DOCXLoader)
    
    with pytest.raises(UnsupportedFileTypeError):
        DocumentLoaderFactory.get_loader("test.txt")

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        DocumentLoaderFactory.get_loader("does_not_exist.pdf")

def test_docx_extraction():
    filepath = os.path.join(fixtures_dir, "normal.docx")
    if not os.path.exists(filepath):
        pytest.skip("Fixture normal.docx not generated.")
        
    loader = DocumentLoaderFactory.get_loader(filepath)
    doc = loader.load()
    
    assert doc.source_type == "docx"
    assert "John Doe" in doc.clean_text
    assert "• Built ResumeIQ" in doc.lines  # Checks bullet normalization

def test_pdf_extraction():
    filepath = os.path.join(fixtures_dir, "single_page.pdf")
    if not os.path.exists(filepath):
        pytest.skip("Fixture single_page.pdf not generated.")
        
    loader = DocumentLoaderFactory.get_loader(filepath)
    doc = loader.load()
    
    assert doc.source_type == "pdf"
    assert "Jane Smith" in doc.clean_text

def test_empty_docx_error():
    filepath = os.path.join(fixtures_dir, "empty.docx")
    if not os.path.exists(filepath):
        pytest.skip("Fixture empty.docx not generated.")
        
    loader = DocumentLoaderFactory.get_loader(filepath)
    with pytest.raises(EmptyDocumentError):
        loader.load()

def test_empty_pdf_error():
    filepath = os.path.join(fixtures_dir, "empty.pdf")
    if not os.path.exists(filepath):
        pytest.skip("Fixture empty.pdf not generated.")
        
    loader = DocumentLoaderFactory.get_loader(filepath)
    with pytest.raises(EmptyDocumentError):
        loader.load()
