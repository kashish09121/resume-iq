class ResumeIQError(Exception):
    """Base exception for all ResumeIQ errors."""
    pass

class UnsupportedFileTypeError(ResumeIQError):
    """Raised when a file extension is not supported."""
    pass

class DocumentExtractionError(ResumeIQError):
    """Raised when text extraction from a document fails."""
    pass

class EmptyDocumentError(ResumeIQError):
    """Raised when a document contains no extractable text."""
    pass

class ScannedDocumentError(ResumeIQError):
    """Raised when a document appears to be an image-only scanned PDF requiring OCR."""
    pass

class FileSizeExceededError(ResumeIQError):
    """Raised when a file exceeds the maximum allowed size."""
    pass
