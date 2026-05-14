from typing import Any, List, Optional, Sequence
from langchain_core.documents import Document
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain_core.callbacks.manager import Callbacks
from scripts.compressor import ContextCompressor

class LLMLinguaDocumentCompressor(BaseDocumentCompressor):
    """
    Compressor de documentos compatível com LangChain usando LLMLingua.
    """
    model_name: str = "Qwen/Qwen2.5-0.5B"
    compression_rate: float = 5.0
    _compressor: ContextCompressor = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._compressor = ContextCompressor(model_name=self.model_name)

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Comprime os documentos recuperados com base na query.
        """
        if not documents:
            return []

        # Junta o conteúdo de todos os documentos em um único contexto
        full_context = "\n\n".join([doc.page_content for doc in documents])
        
        # Realiza a compressão via LLMLingua
        compressed_output = self._compressor.compress(
            context=full_context,
            question=query,
            compression_rate=self.compression_rate
        )
        
        # O LLMLingua retorna um dicionário com o prompt comprimido.
        # Criamos um novo documento com o conteúdo comprimido.
        compressed_text = compressed_output['compressed_prompt']
        
        # Retornamos um único documento contendo o contexto "destilado"
        return [Document(page_content=compressed_text, metadata={"original_count": len(documents)})]
