"""**Document** module is a collection of classes that handle documents
and their transformations.

"""

from aibaba_ai_core.documents.base import Document
from aibaba_ai_core.documents.compressor import BaseDocumentCompressor
from aibaba_ai_core.documents.transformers import BaseDocumentTransformer

__all__ = ["Document", "BaseDocumentTransformer", "BaseDocumentCompressor"]
