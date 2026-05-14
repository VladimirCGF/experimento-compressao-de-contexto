# Plano de Implementação - Fase 5: Interface Visual (Streamlit)

Este documento descreve os passos técnicos para a criação de uma interface gráfica rica e interativa utilizando **Streamlit**, permitindo que usuários não técnicos executem os benchmarks e visualizem a "mágica" da compressão de contexto em tempo real.

## Objetivo
Transformar o pipeline de terminal em uma aplicação visual que destaque as diferenças entre prompts originais e comprimidos, além de exibir gráficos comparativos de performance de hardware.

---

## Passo 1: Atualização de Dependências
Adicionar as ferramentas de visualização ao projeto.
**Ação:** Incluir no `requirements.txt`:
```text
streamlit
plotly
```

## Passo 2: Estrutura Base da App (`scripts/app.py`)
Criar o ponto de entrada da interface.
**Layout Planejado:**
*   **Sidebar:** Configurações globais (Taxa de compressão, escolha do modelo de inferência).
*   **Corpo Principal:** Sistema de abas (Tabs).
    *   **Aba 1: Playground:** Teste rápido de compressão com texto livre.
    *   **Aba 2: Benchmark:** Execução do cenário A/B com logs em tempo real.
    *   **Aba 3: Métricas:** Gráficos interativos (Plotly) comparando VRAM e Tempo.

## Passo 3: Visualização do Prompt "Destruído"
Uma das partes mais interessantes do projeto é ver o que o LLMLingua manteve.
**Implementação:**
*   Criar uma função que compare o texto original com o comprimido.
*   Utilizar `st.markdown` com cores ou estilos para destacar palavras removidas ou mantidas (Highlighting).

## Passo 4: Integração com Monitoramento em Tempo Real
Em vez de apenas ler o CSV ao final, a interface deve mostrar o uso de recursos durante a inferência.
**Ação:**
*   Adaptar o `SystemMonitor` para ser compatível com o loop do Streamlit.
*   Exibir medidores (Gauges) ou gráficos de linha para o uso de VRAM durante o carregamento do modelo e a geração.

## Passo 5: Modo RAG Visual
Integrar a lógica da Fase 4 (LangChain) na interface.
**Funcionalidade:**
*   Upload de arquivos PDF/TXT pelo usuário.
*   Visualização dos fragmentos recuperados do Vector Store.
*   Exibição do prompt final consolidado (e comprimido) enviado ao modelo.

---

## Diferenciais da Interface (UX)
*   **Luzes de Status:** Indicadores visuais se a GPU está ativa ou se houve limpeza de memória.
*   **Download de Relatório:** Botão para exportar os resultados da sessão atual em PDF ou CSV.
*   **Comparador Lado a Lado:** Duas colunas exibindo a resposta do Cenário A e Cenário B simultaneamente para verificação de qualidade rápida.

---

## Critérios de Conclusão da Fase 5
- [ ] Aplicação Streamlit inicia sem erros via `streamlit run scripts/app.py`.
- [ ] Usuário consegue alterar a taxa de compressão via slider e ver o impacto imediato no tamanho do prompt.
- [ ] Gráficos do Plotly exibindo de forma clara a economia de recursos (especialmente VRAM Peak).
- [ ] Interface integrada com os módulos de inferência local (4-bit).
