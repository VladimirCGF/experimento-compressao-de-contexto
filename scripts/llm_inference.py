# pyrefly: ignore [missing-import]
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
import torch

class LocalLLM:
    def __init__(self, model_id="Qwen/Qwen2.5-7B-Instruct"):
        """
        Inicializa o modelo localmente com quantização 4-bit explícita.
        """
        print(f"[Inference] Carregando LLM local: {model_id} (em 4-bit via BitsAndBytes)")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Configuração explícita de quantização 4-bit
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            quantization_config=quantization_config
        )
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        
    def generate_response(self, prompt, max_new_tokens=512):
        """
        Recebe um prompt (comprimido ou original) e gera a resposta utilizando 
        o formato de chat adequado do Llama-3.
        """
        # Formatando as mensagens para o template de chat do modelo
        # O system prompt foi removido para que o prompt (original ou comprimido)
        # seja a única fonte de instrução, garantindo um teste A/B perfeito.
        messages = [
            {
                "role": "user", 
                "content": prompt
            },
        ]
        
        prompt_formatted = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Configurações de geração ajustadas para ser conciso e coerente
        outputs = self.pipe(
            prompt_formatted,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1
        )
        
        # O pipeline retorna todo o texto (prompt + resposta). Precisamos extrair apenas a resposta.
        response = outputs[0]["generated_text"][len(prompt_formatted):]
        return response.strip()
