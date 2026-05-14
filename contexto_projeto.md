# PRD 

Documento de Requisitos de Produto (PRD)

Versão: 2.0.

# 1. Visão Geral do Produto

## Nome do Produto
Context Compression Benchmark (LLMLingua)

## Resumo Executivo
Uma ferramenta de benchmarking avançada para avaliar ganhos de eficiência (redução de VRAM, latência e custos) ao utilizar técnicas de compressão de prompt (LLMLingua). O sistema integra-se ao ecossistema LangChain para RAG (Retrieval-Augmented Generation) e oferece uma interface visual rica para exploração de resultados.

# 2. Problema de Negócio
- **Gargalo de Contexto**: Modelos de linguagem possuem limites de janelas de contexto que aumentam custos e latência de forma quadrática ($O(N^2)$).
- **Consumo de VRAM**: Processar documentos longos localmente frequentemente causa erros de "Out of Memory" (OOM).
- **Ruído Semântico**: Documentos longos contêm muitos tokens de baixa informação que prejudicam a atenção do modelo ("Lost in the Middle").

# 3. Objetivo do Produto
Validar empiricamente que a compressão de contexto pode reduzir drasticamente o consumo de recursos sem comprometer a qualidade da resposta, fornecendo ferramentas para integração em pipelines corporativos (RAG) e visualização de dados.

# 4. Público-Alvo

## Primário
- Desenvolvedores de IA e Engenheiros de Machine Learning.
- Pesquisadores focados em otimização de LLMs.

## Secundário
- Arquitetos de Soluções RAG.
- Desenvolvedores de aplicações que buscam reduzir custos de tokens em APIs.

# 5. Proposta de Valor

## Benefícios principais
- **Economia de Recursos**: Redução comprovada de até 5x no tamanho do contexto.
- **Performance Local**: Viabiliza o uso de modelos de 7B-8B em GPUs com 8GB-12GB de VRAM.
- **Integração Corporativa**: Compatibilidade nativa com LangChain.
- **Visualização de Dados**: Interface Streamlit para análise qualitativa e quantitativa imediata.

# 6. Justificativa Tecnológica
- **LLMLingua**: Baseado em teoria da informação, utiliza a perplexidade para identificar tokens descartáveis.
- **Quantização 4-bit (bitsandbytes)**: Essencial para rodar modelos SOTA em hardware doméstico.
- **Monkey-Patching**: Solução de compatibilidade implementada para lidar com conflitos entre `transformers` e `llmlingua`.

# 7. Benchmark de Modelos no Projeto

| Papel | Modelo | Motivo da Escolha |
|---|---|---|
| **Inferência** | `Qwen2.5-7B-Instruct` | SOTA em performance para modelos compactos e excelente suporte a português. |
| **Compressão** | `Qwen2.5-0.5B` | Extremamente leve, compartilhando o mesmo tokenizer do modelo de inferência (alinhamento semântico). |

# 12. Hardware Alvo
- **GPU**: NVIDIA (Mínimo 8GB VRAM com CUDA).
- **RAM**: 16GB+.
- **SO**: Windows (Facilitado via PowerShell) ou Linux.

# 8. Funcionalidades Principais
- [x] **Benchmark A/B**: Comparação direta entre prompt puro e comprimido.
- [x] **Integração RAG**: Retriever customizado para LangChain (`LLMLinguaDocumentCompressor`).
- [x] **Interface Gráfica**: Dashboard interativo em Streamlit com gráficos Plotly.
- [x] **Telemetria**: Monitoramento em tempo real de CPU, RAM e VRAM (PyTorch peak).
- [x] **Extração Automática**: Scraping de dados da Wikipedia e integração de textos bíblicos (Salmos 91).

# 9. Requisitos Funcionais
- [x] O sistema deve carregar modelos quantizados em 4-bit via HuggingFace.
- [x] O sistema deve calcular a taxa de compressão e tempo de execução.
- [x] O sistema deve gerar relatórios em CSV e JSON.
- [x] A interface Streamlit deve permitir a limpeza de cache de VRAM.

# 10. Requisitos Não Funcionais
- **Confiabilidade**: Limpeza de memória (`gc` e `cuda.empty_cache`) entre execuções.
- **Usabilidade**: Scripts modulares com separação clara de responsabilidades.
- **Performance**: Compressão não deve demorar mais que o ganho de tempo obtido na inferência.

# 11. Arquitetura Proposta

| Camada | Componentes |
|---|---|
| **Visual** | `scripts/app.py` (Streamlit + Plotly) |
| **Integração** | `scripts/langchain_llm.py`, `scripts/langchain_compressor.py` |
| **Core** | `scripts/llm_inference.py`, `scripts/compressor.py` |
| **Orquestração** | `scripts/benchmark.py`, `scripts/benchmark_rag.py` |
| **Monitoramento** | `scripts/utils.py` |

# 13. Métricas de Sucesso
- **TCA**: Taxa de compressão >= 5.0x no cenário B.
- **Latência**: Redução de tempo no "Pre-fill" do cenário B.
- **VRAM**: Pico de memória inferior no cenário B durante a inferência.
- **Fidelidade**: Resposta do cenário B deve conter os fatos principais do texto original.

# 14. Roadmap
- [x] **Fase 1**: Setup e Quantização 4-bit.
- [x] **Fase 2**: Orquestrador A/B e Telemetria.
- [x] **Fase 3**: Geração de Relatórios e Análise Técnica.
- [x] **Fase 4**: Integração com LangChain e Pipelines RAG.
- [x] **Fase 5**: Interface Visual Rica (Streamlit).
- [ ] **Fase 6**: Suporte a modelos Multimodais e compressão de imagens.

# 15. Riscos
- **Alucinação**: Taxas de compressão extremas podem omitir nomes e datas.
- **Compatibilidade**: Quebras futuras em bibliotecas de terceiros (Transformers).
- **Hardware**: Dependência de GPUs NVIDIA para quantização otimizada.

# 16. Entrega Esperada
Um repositório robusto com scripts de terminal, uma interface web operacional e documentação técnica acadêmica comprovando os benefícios da técnica.

# 17. Critério de Avaliação
1. O comando `python -m streamlit run scripts/app.py` deve iniciar o dashboard.
2. O arquivo `benchmark_metrics.csv` deve refletir a economia de VRAM.
3. As respostas do modelo comprimido devem manter coerência com a pergunta original.

---
**Estado Atual dos Arquivos (Checklist):**
- [x] `scripts/app.py` -> Interface Visual.
- [x] `scripts/langchain_compressor.py` -> Módulo RAG.
- [x] `scripts/benchmark_rag.py` -> Teste de RAG.
- [x] `outputs/respostas_comparativas.json` -> Resultados salvos.
- [x] `run.ps1` -> Facilitador de execução.
