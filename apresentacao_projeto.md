# Análise Técnica e Estrutura de Apresentação: Experimento de Compressão de Contexto

Este documento detalha a análise completa do projeto de benchmarking de compressão de prompt utilizando **LLMLingua**, estruturado para uma apresentação técnica em slides.

---

## 1. Introdução do Projeto
*   **Nome do Projeto:** Context Compression Benchmark (LLMLingua).
*   **Problema que resolve:** O "gargalo" de contexto e o alto custo computacional (latência e memória) ao processar documentos extensos em Large Language Models (LLMs).
*   **Contexto de Uso:** Sistemas de RAG (Retrieval-Augmented Generation), assistentes virtuais de leitura de documentos longos e processamento de logs extensos.
*   **Público-alvo:** Desenvolvedores de IA, pesquisadores e arquitetos de sistemas que buscam otimizar custos e performance de modelos locais.
*   **Objetivo Principal:** Avaliar empiricamente o impacto da técnica de compressão de contexto na eficiência de hardware (VRAM, Tempo) e na fidelidade da resposta gerada por um modelo local de 7 bilhões de parâmetros.

---

## 2. Visão Geral da Solução
*   **Funcionamento:** O sistema executa um teste A/B comparativo. O cenário A processa o texto integral; o cenário B aplica uma técnica baseada em teoria da informação para descartar tokens redundantes antes da inferência.
*   **Módulos:**
    *   **Data Ingestion:** Coleta automática de dados (Wikipedia/Textos fixos).
    *   **Compression Engine:** Wrapper sobre o framework LLMLingua.
    *   **Inference Engine:** Executor local de modelos quantizados.
    *   **Monitoramento:** Captura de métricas de hardware em tempo real.
*   **Interação:** O usuário define a pergunta e o contexto; o backend orquestra a compressão, a inferência e devolve um relatório comparativo detalhado.

---

## 3. Arquitetura do Sistema
*   **Arquitetura Utilizada:** Pipeline de processamento sequencial e modular.
*   **Padrão Arquitetural:** Wrapper Pattern / Service-Oriented (em scripts).
*   **Comunicação:** Chamadas funcionais entre classes especializadas (`ContextCompressor`, `LocalLLM`, `SystemMonitor`).
*   **Persistência:** Exportação de resultados em `outputs/` via JSON (auditável) e CSV (quantitativo).
*   **Autenticação:** Opcional via Hugging Face Hub (configurada via variáveis de ambiente/CLI).
*   **Estrutura de Diretórios:**
    *   `/scripts`: Lógica de negócio e wrappers.
    *   `/data`: Armazenamento temporário de contextos.
    *   `/outputs`: Relatórios finais.
*   **Escolha da Arquitetura:** Focada em **reprodutibilidade acadêmica**. A separação modular permite trocar o modelo de compressão (ex: Qwen-0.5B por Phi-2) ou o modelo de inferência (ex: Llama-3 por Mistral) sem alterar o pipeline de benchmark.

---

## 4. Tecnologias Utilizadas

| Tecnologia | Uso no Projeto | Vantagens | Desvantagens |
| :--- | :--- | :--- | :--- |
| **Python** | Linguagem Base | Ecossistema vasto para IA. | Performance em loopings puros (não crítico aqui). |
| **LLMLingua** | Compressão de Prompt | Redução de até 20x no tamanho do contexto. | Pequeno overhead de tempo inicial. |
| **Hugging Face** | Modelos e Pipelines | Acesso a SOTA (Qwen2.5/Llama-3). | Dependência de conectividade/infra. |
| **BitsAndBytes** | Quantização 4-bit | Redução drástica de VRAM (roda em GPUs domésticas). | Pequena perda de precisão teórica. |
| **Psutil** | Monitoramento | Precisão na medição de RAM/CPU. | Variações dependendo do SO. |

---

## 5. Funcionalidades do Sistema
*   **Compressão Inteligente:** Utiliza um modelo pequeno para calcular a perplexidade de cada token e remover o que for estatisticamente irrelevante.
*   **Inferência Local 4-bit:** Carregamento de modelos de 7B-14B parâmetros em GPUs com apenas 8GB-12GB de VRAM.
*   **Hardware Profiling:** Relatório automático de pico de VRAM, uso de CPU e tempo de execução por cenário.
*   **Auditoria de Resposta:** Salva o prompt "destruído" pela compressão para análise qualitativa humana.

---

## 6. Fluxo de Funcionamento
1.  **Entrada:** Carregamento do texto base (ex: Guerra de Canudos ou Salmos 91) e pergunta.
2.  **Processamento (B):** O modelo `Qwen-0.5B` analisa o texto e gera a versão comprimida.
3.  **Comunicação:** O prompt comprimido é enviado via pipeline `transformers` para a GPU.
4.  **Inferência:** O modelo `Qwen-7B` processa os tokens e gera a resposta.
5.  **Persistência:** As métricas são gravadas em CSV e as respostas em JSON.
6.  **Retorno:** Exibição do resumo comparativo no terminal para o pesquisador.

---

## 7. Modelagem e Estrutura das Entidades
*   **Classes Principais:**
    *   `ContextCompressor`: Gerencia o `PromptCompressor` e configurações de taxa de compressão.
    *   `LocalLLM`: Encapsula o modelo e tokenizer, lidando com `chat_templates` e quantização.
    *   `SystemMonitor`: Responsável pela telemetria de hardware usando `psutil` e `torch.cuda`.
*   **Responsabilidades:**
    *   **Services:** `fetch_data.py` atua como serviço de obtenção de dados externos.
    *   **Controllers/Orchestrators:** `benchmark.py` coordena o ciclo de vida dos modelos para evitar vazamento de memória.

---

## 8. Comparações Técnicas

### LLMLingua vs Truncamento Simples
*   **LLMLingua:** Mantém os tokens de alta informação (verbos, nomes próprios).
*   **Truncamento:** Simplesmente corta o final do texto, perdendo contexto essencial.
*   **Escolha:** LLMLingua permite que o modelo "veja" o documento inteiro de forma resumida.

### 4-bit (NF4) vs 16-bit (Float16)
*   **4-bit:** Ocupa ~5.5GB de VRAM para um modelo 7B.
*   **16-bit:** Ocuparia ~14GB de VRAM.
*   **Escolha:** 4-bit possibilita a execução em hardware acessível sem comprometer a lógica da resposta.

---

## 9. Vantagens do Projeto
*   **Produtividade:** Redução do tempo de espera por token em contextos longos.
*   **Eficiência de Custo:** Menor número de tokens enviados para APIs (se utilizado comercialmente).
*   **Portabilidade:** Execução totalmente offline em workstations padrão.
*   **Experiência do Usuário:** Respostas mais rápidas mesmo sob condições de hardware limitadas.

---

## 10. Desvantagens e Limitações
*   **Gargalo de Compressão:** Para textos pequenos, o tempo para comprimir pode ser maior que a economia na inferência.
*   **Risco de Alucinação:** Se a taxa de compressão for agressiva demais (>10x), tokens vitais podem ser perdidos.
*   **Dependência de GPU:** Ainda requer hardware NVIDIA para performance aceitável devido ao `bitsandbytes`.

---

## 11. Melhorias Futuras
*   **Interface Gráfica (Streamlit):** Visualização em tempo real das métricas e nuvens de palavras dos tokens removidos.
*   **Integração com LangChain:** Criar um nó de compressão dinâmico para pipelines RAG.
*   **Multi-Model Support:** Testar automaticamente contra GPT-4o-mini para validar a qualidade da resposta.
*   **Cloud Deployment:** Containerização com Docker para execução em instâncias spot de baixo custo.

---

## 12. Conclusão
O projeto demonstra que a compressão de contexto não é apenas uma curiosidade técnica, mas uma necessidade estratégica para a viabilização de LLMs locais. O experimento prova que é possível manter a coerência da resposta reduzindo drasticamente o consumo de recursos, pavimentando o caminho para aplicações de IA mais sustentáveis e rápidas.

---
**Nota Técnica:** As métricas obtidas indicam que o cenário comprimido (5x) mantém a precisão factual enquanto libera recursos de hardware para processamento paralelo.
