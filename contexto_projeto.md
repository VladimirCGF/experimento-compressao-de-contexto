# PRD 

Documento de Requisitos de Produto (PRD)

Versão: 2.5.

# 1. Visão Geral do Produto

## Nome do Produto
Context Compression Benchmark (LLMLingua)

## Resumo Executivo
Uma plataforma de benchmarking e playground para otimização de contextos em Modelos de Linguagem de Larga Escala (LLMs). O sistema utiliza a técnica **LLMLingua** para comprimir prompts em até 5x-10x, reduzindo drasticamente o consumo de VRAM e a latência de inferência em hardware local, sem perda significativa de fidelidade semântica.

# 2. Problema de Negócio
- **Custo Computacional**: Inferência em contextos longos (RAG) é lenta e consome VRAM de forma proibitiva para hardware doméstico.
- **Limites de Janela**: Documentos extensos frequentemente excedem o limite de tokens dos modelos.
- **Ruído Semântico**: Tokens irrelevantes em documentos recuperados aumentam a distração do modelo ("Lost in the Middle").

# 3. Objetivo do Produto
Prover uma ferramenta modular para validar e integrar compressão de contexto em pipelines de IA, permitindo que modelos de 7B+ parâmetros operem eficientemente em GPUs de entrada/intermediárias (8GB-12GB VRAM).

# 4. Público-Alvo

## Primário
- Engenheiros de IA/ML focados em otimização local.
- Desenvolvedores de sistemas RAG.

## Secundário
- Pesquisadores acadêmicos em Processamento de Linguagem Natural (NLP).
- Empresas buscando reduzir custos de tokens em provedores de nuvem.

# 5. Proposta de Valor

## Benefícios principais
- [x] **Eficiência**: Redução de até 80% no tamanho do prompt.
- [x] **Economia**: Menor uso de memória de vídeo (VRAM) via KV-Cache otimizado.
- [x] **Velocidade**: Aceleração do tempo de "First Token" (Pre-fill).
- [x] **Acurácia**: Manutenção da qualidade da resposta através de seleção inteligente de tokens.

# 6. Justificativa Tecnológica
- **LLMLingua/PromptCompressor**: Utiliza a perplexidade de um modelo pequeno (0.5B) para remover tokens de baixa informação.
- **Quantização 4-bit (bitsandbytes)**: Permite rodar modelos potentes (7B) em 5GB-6GB de VRAM.
- **Telemetria Integrada**: Monitoramento de hardware em tempo real para provas de conceito (PoC).

# 7. Benchmark de Modelos no Projeto
| Função | Modelo Selecionado | Justificativa |
|---|---|---|
| **Inferência** | `Qwen2.5-7B-Instruct` | Melhor relação performance/parâmetros atual (SOTA). |
| **Compressão** | `Qwen2.5-0.5B` | Alinhamento de tokenizer com o modelo de inferência. |

# 8. Funcionalidades Principais
- [x] **Dashboard Interativo**: Interface Streamlit para testes A/B.
- [x] **Playground de Compressão**: Comparação em tempo real entre texto puro e comprimido.
- [x] **Análise de Performance**: Gráficos Plotly de latência e pico de VRAM.
- [x] **Integração LangChain**: Módulo `LLMLinguaDocumentCompressor` para pipelines RAG.
- [x] **Gestão de Memória**: Botão para limpeza forçada de cache de VRAM.

# 9. Requisitos Funcionais
- [x] Carregar modelos HuggingFace com `load_in_4bit=True`.
- [x] Suportar entrada de texto via scraping (Wikipedia) ou arquivos locais.
- [x] Exportar métricas de benchmark para CSV/JSON.
- [x] Implementar monitoramento de sistema (`psutil` + `torch.cuda`).

# 10. Requisitos Não Funcionais
- **Modularidade**: Scripts separados para inferência, compressão e utilitários.
- **Performance**: O overhead da compressão deve ser inferior ao ganho de tempo na inferência.
- **UX**: Interface escura (dark mode) com estética premium e responsiva.

# 11. Arquitetura Proposta
| Módulo | Arquivo | Função |
|---|---|---|
| **Frontend** | `scripts/app.py` | UI Streamlit e Dashboard. |
| **Compressão** | `scripts/compressor.py` | Lógica de compressão LLMLingua. |
| **Inferência** | `scripts/llm_inference.py` | Wrapper para Transformers/PyTorch. |
| **RAG** | `scripts/langchain_compressor.py` | Integração com LangChain. |
| **Monitor** | `scripts/utils.py` | Telemetria de hardware. |

# 12. Hardware Alvo
- **GPU**: NVIDIA RTX 3060+ (Mínimo 8GB VRAM).
- **RAM**: 16GB.
- **Drivers**: CUDA 11.8+ instalado.

# 13. Métricas de Sucesso
- **TCA**: Taxa de Compressão Alvo >= 5.0x.
- **VRAM**: Redução de ~15-20% no pico de memória em contextos longos.
- **Fidelidade**: Resposta gerada deve manter a verdade factual do texto original.

# 14. Roadmap
- [x] Setup do ambiente e quantização.
- [x] Implementação do core de compressão.
- [x] Criação do dashboard Streamlit.
- [x] Integração modular com LangChain.
- [ ] Suporte a modelos multimoldais (Vision-Language).
- [ ] Implementação de cache de prompts comprimidos em banco vetorial.

# 15. Riscos
- **Alucinação**: Perda de detalhes finos em taxas de compressão > 10x.
- **Dependências**: Conflitos entre versões de `transformers` e `llmlingua`.
- **Hardware**: Incompatibilidade com GPUs não-NVIDIA (bitsandbytes).

# 16. Entrega Esperada
Repositório completo com pipeline de compressão validado, dashboard de visualização e scripts de integração para sistemas RAG corporativos.

# 17. Critério de Avaliação
1. Sucesso ao executar `python -m streamlit run scripts/app.py`.
2. Geração de resposta coerente no Playground usando 5x de compressão.
3. Redução visível nos gráficos de latência "Pre-fill" para contextos > 2k tokens.

---

**Estado Atual dos Arquivos (Checklist para IA):**
- [x] `scripts/app.py` -> Interface Principal (OK).
- [x] `scripts/compressor.py` -> Engine de Compressão (OK).
- [x] `scripts/llm_inference.py` -> Backend de Inferência (OK).
- [x] `scripts/langchain_compressor.py` -> Plugin RAG (OK).
- [x] `scripts/benchmark_rag.py` -> Script de Teste Automatizado (OK).
- [x] `requirements.txt` -> Dependências atualizadas (OK).
- [x] `run.ps1` -> Automação de execução no Windows (OK).
