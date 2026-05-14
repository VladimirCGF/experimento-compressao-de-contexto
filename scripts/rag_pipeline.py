import os
import torch
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains import RetrievalQA
from scripts.fetch_data import get_salmos_text
from scripts.langchain_llm import HuggingFaceLocalLLM
from scripts.langchain_compressor import LLMLinguaDocumentCompressor

def run_rag_example():
    print("\n" + "="*60)
    print(" INICIANDO PIPELINE RAG COM COMPRESSÃO (LANGCHAIN) ")
    print("="*60)

    # 1. Obtenção e Preparação dos Dados
    print("[1/5] Carregando e segmentando texto...")
    text = get_salmos_text()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, 
        chunk_overlap=50
    )
    docs = text_splitter.create_documents([text])
    print(f"-> Criados {len(docs)} fragmentos de texto.")

    # 2. Criação do Vector Store (Embeddings)
    print("[2/5] Gerando embeddings e indexando no FAISS...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 3. Inicialização dos Componentes Customizados
    print("[3/5] Inicializando Compressor e LLM Local...")
    compressor = LLMLinguaDocumentCompressor(compression_rate=3.0)
    llm = HuggingFaceLocalLLM()

    # 4. Configuração do Retriever com Compressão
    print("[4/5] Configurando ContextualCompressionRetriever...")
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=base_retriever
    )

    # 5. Execução da Chain de QA
    print("[5/5] Executando consulta no pipeline RAG...")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=compression_retriever
    )

    query = "O que acontece com quem pisa o leão e a cobra segundo o texto?"
    print(f"\nPergunta: {query}")
    
    response = qa_chain.invoke(query)
    
    print("\n" + "-"*40)
    print(" RESPOSTA FINAL (RAG + COMPRESSÃO) ")
    print("-"*40)
    print(response["result"])
    print("-"*40)

if __name__ == "__main__":
    # Limpeza de memória antes de começar
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    run_rag_example()
