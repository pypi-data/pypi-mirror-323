from langtxt.document_loaders.directory import DirectoryLoader
from langtxt.document_loaders.docx import DocxLoader
from langtxt.document_loaders.html import HTMLLoader
from langtxt.document_loaders.json import JSONLoader
from langtxt.document_loaders.pdf import PDFLoader
from langtxt.document_loaders.s3 import S3Loader
from langtxt.document_loaders.watson_discovery import WatsonDiscoveryLoader

__all__ = [
    "DirectoryLoader",
    "DocxLoader",
    "HTMLLoader",
    "JSONLoader",
    "PDFLoader",
    "S3Loader",
    "WatsonDiscoveryLoader",
]
