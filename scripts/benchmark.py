import os
import json
import gc
import torch
import pandas as pd
from utils import SystemMonitor
from fetch_data import get_salmos_text
from compressor import ContextCompressor
from llm_inference import LocalLLM

# Obtém caminho absoluto da raiz do projeto para salvar as saídas corretamente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

def cleanup_memory():
    """Força limpeza de memória RAM e VRAM (MUITO importante para evitar Out of Memory)."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("="*60)
    print(" INICIANDO BENCHMARK DE COMPRESSÃO DE CONTEXTO (LLMLINGUA) ")
    print("="*60)
    
    # 1. Obtenção do Texto
    print("\n[Passo 1] Carregando texto base (Salmos 91)...")
    context = get_salmos_text()
    question = "Quais são as principais promessas de proteção descritas neste texto e qual a condição para recebê-las?"
    
    monitor = SystemMonitor()
    results = []
    
    # Vamos instanciar o LLM principal uma única vez
    print("\n[Passo 2] Preparando Modelo Principal de Inferência...")
    llm = LocalLLM(model_id="Qwen/Qwen2.5-7B-Instruct")
    
    # ---------------------------------------------------------
    # CENÁRIO A: TEXTO ORIGINAL (SEM COMPRESSÃO)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print(" CENÁRIO A: INFERÊNCIA COM TEXTO ORIGINAL ")
    print("-"*40)
    
    instruction = "Você é um assistente útil e especialista. Responda à pergunta baseando-se estritamente no texto fornecido."
    
    # O prompt do Cenário A agora replica a EXATA mesma estrutura gerada pelo LLMLingua (Cenário B)
    prompt_original = f"{instruction}\n\n{context}\n\n{question}"
    original_tokens = len(llm.tokenizer.encode(prompt_original))
    print(f"-> Tokens de entrada (Original): {original_tokens}")
    
    cleanup_memory()
    monitor.start()
    
    print("Gerando resposta...")
    response_original = llm.generate_response(prompt_original)
    
    metrics_a = monitor.stop()
    metrics_a.update({
        "cenario": "A_Sem_Compressao",
        "tokens_entrada": original_tokens,
        "taxa_compressao_alcancada": "1.00x",
        "tamanho_resposta_chars": len(response_original),
        "tempo_compressao_seg": 0.0,
        "tempo_inferencia_seg": metrics_a["time_seconds"]
    })
    results.append(metrics_a)
    
    print(f"\n[Trecho da Resposta A (Original)]:\n{response_original[:400]}...\n")
    
    # ---------------------------------------------------------
    # CENÁRIO B: TEXTO COMPRIMIDO (LLMLINGUA - 5x)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print(" CENÁRIO B: INFERÊNCIA COM TEXTO COMPRIMIDO (5x) ")
    print("-"*40)
    
    print("Carregando Compressor de Contexto (Qwen-0.5B)...")
    # Carrega o modelo de compressão localmente
    compressor = ContextCompressor(model_name="Qwen/Qwen2.5-0.5B") 
    
    cleanup_memory()
    monitor.start()
    
    print("Comprimindo o prompt original...")
    compressed_dict = compressor.compress(context, question, compression_rate=5.0)
    compress_time = monitor.stop()["time_seconds"]
    
    compressed_prompt_text = compressed_dict['compressed_prompt']
    compressed_tokens_count = compressed_dict['compressed_tokens']
    origin_tokens_count = compressed_dict['origin_tokens']
    
    print(f"-> Tokens originais vistos pelo compressor: {origin_tokens_count}")
    print(f"-> Tokens finais após compressão: {compressed_tokens_count}")
    print(f"-> Taxa de compressão real: {origin_tokens_count/max(1, compressed_tokens_count):.2f}x")
    
    print("\n[Amostra do Prompt Comprimido (Observe a 'estranheza' do texto)]:")
    print("*" * 50)
    print(compressed_prompt_text[:500] + "\n[...] (texto truncado para exibição)")
    print("*" * 50)
    
    # Libera o compressor da VRAM para que o LLM principal tenha espaço total na inferência
    del compressor
    cleanup_memory()
    
    # Inferência com prompt comprimido
    monitor.start()
    print("\nGerando resposta com o prompt comprimido...")
    response_compressed = llm.generate_response(compressed_prompt_text)
    
    metrics_b = monitor.stop()
    
    # Calculando taxa exata usando o tokenizer do Llama-3
    llama_tokens_compressed = len(llm.tokenizer.encode(compressed_prompt_text))
    
    metrics_b.update({
        "cenario": "B_Com_Compressao_5x",
        "tokens_entrada": llama_tokens_compressed,
        "taxa_compressao_alcancada": f"{original_tokens / max(1, llama_tokens_compressed):.2f}x",
        "tamanho_resposta_chars": len(response_compressed),
        "tempo_compressao_seg": compress_time,
        "tempo_inferencia_seg": metrics_b["time_seconds"]
    })
    
    # O tempo total da operação = tempo de compressão + tempo de inferência
    metrics_b["time_seconds"] += compress_time 
    results.append(metrics_b)
    
    print(f"\n[Trecho da Resposta B (Comprimido)]:\n{response_compressed[:400]}...\n")
    
    # ---------------------------------------------------------
    # SALVAR RESULTADOS
    # ---------------------------------------------------------
    print("\n[Passo 3] Salvando e consolidando resultados...")
    
    # Salva JSON detalhado com os prompts e respostas literais
    respostas_json = {
        "metadados": {
            "pergunta": question,
            "modelo_inferencia": "Qwen/Qwen2.5-7B-Instruct",
            "modelo_compressao": "Qwen/Qwen2.5-0.5B",
        },
        "cenario_A_Original": {
            "prompt_amostra": prompt_original[:1000] + "...",
            "resposta_completa": response_original
        },
        "cenario_B_Comprimido": {
            "prompt_amostra": compressed_prompt_text[:1000] + "...",
            "resposta_completa": response_compressed
        }
    }
    
    json_path = os.path.join(OUTPUT_DIR, "respostas_comparativas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(respostas_json, f, indent=4, ensure_ascii=False)
        
    # Salva DataFrame CSV com as métricas quantitativas de uso de recursos
    df = pd.DataFrame(results)
    cols = [
        "cenario", "tokens_entrada", "taxa_compressao_alcancada",
        "time_seconds", "tempo_compressao_seg", "tempo_inferencia_seg",
        "cpu_percent", "ram_used_mb", "vram_peak_mb", "tamanho_resposta_chars"
    ]
    df = df[cols]
    
    csv_path = os.path.join(OUTPUT_DIR, "benchmark_metrics.csv")
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*60)
    print(" RESUMO FINAL DO BENCHMARK ")
    print("="*60)
    print(df.to_string(index=False))
    print(f"\nArquivos salvos com sucesso em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
