import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
import pdfminer.high_level

from resume_iq.ingestion.models import PreprocessedDocument
from resume_iq.ingestion.exceptions import (
    UnsupportedFileTypeError,
    DocumentExtractionError,
    EmptyDocumentError,
    ScannedDocumentError,
    FileSizeExceededError
)
from resume_iq.preprocessing.cleaner import TextCleaner
from resume_iq.config.settings import settings

class BaseLoader:
    """Base class for document loaders."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._validate_file()

    def _validate_file(self):
        """Validate file existence and size constraints."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
            
        file_size_mb = os.path.getsize(self.filepath) / (1024 * 1024)
        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise FileSizeExceededError(
                f"File size ({file_size_mb:.1f}MB) exceeds maximum limit ({settings.MAX_UPLOAD_SIZE_MB}MB)"
            )

    def extract_raw_text(self) -> str:
        raise NotImplementedError

    def load(self) -> PreprocessedDocument:
        """Load, extract, clean, and return a PreprocessedDocument."""
        raw_text = self.extract_raw_text()
        
        # Check for empty extraction
        if not raw_text.strip():
            raise EmptyDocumentError("Document contains no extractable text.")
            
        # Clean text
        clean_text = TextCleaner.clean(raw_text)
        
        if not clean_text.strip():
             raise EmptyDocumentError("Document contains no extractable text after cleaning.")

        return PreprocessedDocument(
            source_name=os.path.basename(self.filepath),
            source_type=self.__class__.__name__.replace("Loader", "").lower(),
            raw_text=raw_text,
            clean_text=clean_text,
            lines=clean_text.splitlines(),
            metadata={"file_size_bytes": os.path.getsize(self.filepath)}
        )

class PDFLoader(BaseLoader):
    """Loader for extracting text from PDF files."""
    
    def extract_raw_text(self) -> str:
        try:
            raw_text = pdfminer.high_level.extract_text(self.filepath)
            
            # Scanned PDF heuristic: If text is extremely short but file is large
            if len(raw_text.strip()) < 20 and os.path.getsize(self.filepath) > 50000:
                raise ScannedDocumentError(
                    "No extractable text detected. The document may be scanned/image-based and may require OCR."
                )
                
            return raw_text
        except ScannedDocumentError:
            raise
        except Exception as e:
            raise DocumentExtractionError(f"Failed to extract PDF: {str(e)}") from e

class DOCXLoader(BaseLoader):
    """
    Loader for extracting text from DOCX files.
    Implemented using pure Python standard libraries (zipfile, xml.etree.ElementTree)
    to avoid C-extension DLL blocks (e.g., AppLocker blocking lxml used by python-docx).
    """
    
    def extract_raw_text(self) -> str:
        try:
            text_blocks = []
            with zipfile.ZipFile(self.filepath) as docx:
                xml_content = docx.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                
                # XML namespace for Word
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                for paragraph in tree.findall('.//w:p', namespaces=ns):
                    texts = [node.text for node in paragraph.findall('.//w:t', namespaces=ns) if node.text]
                    if texts:
                        text_blocks.append(''.join(texts))
                        
            return "\n".join(text_blocks)
        except Exception as e:
            raise DocumentExtractionError(f"Failed to extract DOCX: {str(e)}") from e

class DocumentLoaderFactory:
    """Factory to dispatch to the correct loader based on file extension."""
    
    @staticmethod
    def get_loader(filepath: str) -> BaseLoader:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            return PDFLoader(filepath)
        elif ext == ".docx":
            return DOCXLoader(filepath)
        else:
            raise UnsupportedFileTypeError(
                f"Unsupported file extension '{ext}'. Supported formats: {', '.join(settings.SUPPORTED_EXTENSIONS)}"
            )
