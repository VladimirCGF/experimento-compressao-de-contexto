# Plano de Implementação - Fase 4: Integração com LangChain e RAG

Este documento descreve os passos técnicos necessários para atingir o objetivo da Fase 4 do Roadmap: integrar a engine de compressão de contexto ao ecossistema corporativo do **LangChain** para uso em pipelines de **Retrieval-Augmented Generation (RAG)**.

## Objetivo
Transformar as ferramentas desenvolvidas em scripts procedurais em classes compatíveis com a arquitetura padrão da indústria (LangChain), permitindo que a compressão atue de forma transparente no fluxo de recuperação de documentos (Retriever).

---

## Passo 1: Atualização das Dependências
Antes de iniciar a refatoração, precisaremos adicionar os pacotes do ecossistema LangChain.
**Ação:** Atualizar o arquivo `requirements.txt` com as seguintes bibliotecas:
```text
langchain
langchain-community
langchain-huggingface
faiss-cpu          # Para simular um Vector Database local leve
sentence-transformers # Para embeddings do RAG
```

## Passo 2: Criação do Wrapper do LLM (`scripts/langchain_llm.py`)
Atualmente, a classe `LocalLLM` é isolada. Precisamos envelopá-la para que o LangChain a reconheça como um modelo padrão.
**Implementação:**
1. Criar a classe `HuggingFaceLocalLLM` estendendo `LLM` (ou usar a implementação nativa `HuggingFacePipeline` da biblioteca `langchain-huggingface`).
2. Garantir que a configuração 4-bits (`BitsAndBytesConfig`) seja passada adequadamente na inicialização do pipeline do LangChain.

## Passo 3: Criação do Compressor de Documentos LangChain (`scripts/langchain_compressor.py`)
O LangChain possui uma interface nativa para compressão de documentos: `BaseDocumentCompressor`. Esta é a parte central da Fase 4.
**Implementação:**
1. Criar a classe `LLMLinguaDocumentCompressor` herdando de `BaseDocumentCompressor` do pacote `langchain.retrievers.document_compressors`.
2. O método obrigatório `compress_documents(documents, query)` deve:
    * Agrupar o conteúdo dos documentos recuperados.
    * Chamar a instância do `PromptCompressor` (do LLMLingua) passando a `query` (pergunta do usuário).
    * Retornar uma nova lista de `Document` com o conteúdo reduzido e os metadados preservados.

## Passo 4: Pipeline RAG Completo (`scripts/rag_pipeline.py`)
Criar o script principal que simula o caso de uso corporativo completo.
**Fluxo do Script:**
1. **Ingestão:** Carregar um texto longo, "quebrá-lo" usando `RecursiveCharacterTextSplitter` e converter em Embeddings armazenados no FAISS.
2. **Base Retriever:** Criar o retriever padrão buscando os top-K documentos (ex: Top 10). *Problema original: 10 documentos estourariam o contexto.*
3. **Compression Retriever:** Instanciar um `ContextualCompressionRetriever`, passando o `Base Retriever` e o nosso novo `LLMLinguaDocumentCompressor`.
4. **QA Chain:** Montar a chain de Pergunta e Resposta ligando o `Compression Retriever` ao `HuggingFaceLocalLLM`.

## Passo 5: Avaliação e Benchmark RAG (`scripts/benchmark_rag.py`)
Atualizar nosso orquestrador de benchmark para suportar a nova arquitetura.
**Ação:**
1. Rodar a Pergunta no Pipeline RAG sem compressor (capturar OOM ou latência altíssima do pre-fill dos 10 documentos).
2. Rodar a Pergunta no Pipeline RAG com `ContextualCompressionRetriever` (capturar latência e redução de payload).
3. Salvar os resultados em um novo arquivo: `outputs/rag_benchmark_metrics.csv`.

---

## Critérios de Conclusão da Fase 4
- [ ] Módulo `langchain_compressor.py` implementado e compatível com a API do LangChain.
- [ ] Pipeline RAG funcionando ponta a ponta recuperando documentos de um Vector Store local.
- [ ] Evidência (via logs ou CSV) de que múltiplos documentos recuperados (ex: 5 páginas) foram condensados em um contexto reduzido antes de serem enviados ao modelo 7B.
- [ ] Resposta final (gerada via RAG) mantendo coerência com os fragmentos originais recuperados e comprimidos.
