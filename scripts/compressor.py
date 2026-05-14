from llmlingua import PromptCompressor
import torch

# --- INÍCIO DO MONKEY PATCH ---
# Corrige o bug de incompatibilidade entre LLMLingua e transformers >= 4.38
try:
    from transformers.cache_utils import DynamicCache
    original_iter = DynamicCache.__iter__
    def patched_iter(self):
        for item in original_iter(self):
            # O transformers novo retorna 3 itens, mas o llmlingua espera apenas 2 (k, v)
            if len(item) >= 2:
                yield item[0], item[1]
            else:
                yield item
    DynamicCache.__iter__ = patched_iter
except ImportError:
    pass
# --- FIM DO MONKEY PATCH ---

class ContextCompressor:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B"):
        """
        Inicializa o compressor usando o Qwen-0.5B.
        O Monkey Patch acima garante que ele funcionará perfeitamente.
        """
        print(f"[Compressor] Carregando modelo de compressão: {model_name}")
        self.compressor = PromptCompressor(
            model_name=model_name,
            device_map="auto" if torch.cuda.is_available() else "cpu"
        )
        
    def compress(self, context, question, compression_rate=5.0):
        """
        Aplica o LLMLingua para remover tokens redundantes.
        """
        instruction = "Você é um assistente útil e especialista. Responda à pergunta baseando-se estritamente no texto fornecido."
        target_rate = 1.0 / compression_rate
        
        compressed_prompt = self.compressor.compress_prompt(
            context=[context],
            instruction=instruction,
            question=question,
            rate=target_rate,
            condition_in_question='after_condition',
            reorder_context='sort',
            use_sentence_level_filter=False
        )
        
        return compressed_prompt
