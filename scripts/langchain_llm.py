from typing import Any, List, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from scripts.llm_inference import LocalLLM

class HuggingFaceLocalLLM(LLM):
    """
    Wrapper customizado para o LocalLLM (Qwen-7B-4bit) funcionar no LangChain.
    """
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    _local_llm: LocalLLM = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializa o modelo local apenas uma vez
        self._local_llm = LocalLLM(model_id=self.model_id)

    @property
    def _llm_type(self) -> str:
        return "custom_huggingface_local"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            # Implementação simples de stop tokens se necessário
            pass
        
        return self._local_llm.generate_response(prompt)

    @property
    def _identifying_params(self) -> dict:
        return {"model_id": self.model_id}
