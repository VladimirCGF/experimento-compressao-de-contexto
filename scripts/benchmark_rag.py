import os
import time
import pandas as pd
import torch
import gc
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains import RetrievalQA

from scripts.fetch_data import get_salmos_text
from scripts.langchain_llm import HuggingFaceLocalLLM
from scripts.langchain_compressor import LLMLinguaDocumentCompressor
from scripts.utils import SystemMonitor

def cleanup():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def run_benchmark():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print(" BENCHMARK RAG: COM COMPRESSÃO VS SEM COMPRESSÃO ")
    print("="*60)

    # Setup inicial
    text = get_salmos_text()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.create_documents([text])
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # K=8 para forçar um contexto razoavelmente grande
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    
    llm = HuggingFaceLocalLLM()
    monitor = SystemMonitor()
    results = []

    query = "Quais as promessas para quem conhece o nome de Deus?"

    # --- CENÁRIO 1: RAG SEM COMPRESSÃO ---
    print("\n[Cenário 1] Executando RAG Tradicional (K=8)...")
    cleanup()
    qa_chain_normal = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=base_retriever)
    
    monitor.start()
    resp_normal = qa_chain_normal.invoke(query)
    metrics_normal = monitor.stop()
    
    metrics_normal.update({
        "cenario": "RAG_Sem_Compressao",
        "query": query,
        "tokens_aprox": "K=8 Docs"
    })
    results.append(metrics_normal)
    print(f"Tempo: {metrics_normal['time_seconds']}s | VRAM Peak: {metrics_normal['vram_peak_mb']}MB")

    # --- CENÁRIO 2: RAG COM COMPRESSÃO LLMLINGUA ---
    print("\n[Cenário 2] Executando RAG com Compressão LLMLingua (Taxa 3x)...")
    cleanup()
    compressor = LLMLinguaDocumentCompressor(compression_rate=3.0)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=base_retriever
    )
    qa_chain_comp = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=compression_retriever)
    
    monitor.start()
    resp_comp = qa_chain_comp.invoke(query)
    metrics_comp = monitor.stop()
    
    metrics_comp.update({
        "cenario": "RAG_Com_Compressao",
        "query": query,
        "tokens_aprox": "K=8 Docs (Comprimidos)"
    })
    results.append(metrics_comp)
    print(f"Tempo: {metrics_comp['time_seconds']}s | VRAM Peak: {metrics_comp['vram_peak_mb']}MB")

    # Consolidação
    df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, "rag_benchmark_metrics.csv")
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*60)
    print(" RESULTADOS DO BENCHMARK RAG SALVOS ")
    print("="*60)
    print(df.to_string(index=False))

if __name__ == "__main__":
    run_benchmark()
