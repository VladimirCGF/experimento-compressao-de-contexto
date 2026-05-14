import streamlit as st
import pandas as pd
import plotly.express as px
import torch
import gc
import os
import sys

# Adiciona o diretório raiz ao path para importar os scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.llm_inference import LocalLLM
from scripts.compressor import ContextCompressor
from scripts.utils import SystemMonitor
from scripts.fetch_data import get_salmos_text

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="LLMLingua Context Compression",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Customizado (Premium Aesthetics)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3e4251;
    }
    .highlight-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #238636;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CACHE DE RECURSOS (MUITO IMPORTANTE PARA VRAM) ---
@st.cache_resource
def load_llm(model_id):
    return LocalLLM(model_id=model_id)

@st.cache_resource
def load_compressor(model_name):
    return ContextCompressor(model_name=model_name)

def cleanup_vram():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configurações")
    st.markdown("---")
    
    model_id = st.selectbox(
        "Modelo de Inferência (7B)",
        ["Qwen/Qwen2.5-7B-Instruct", "meta-llama/Llama-3-8B-Instruct"],
        index=0
    )
    
    compressor_model = st.selectbox(
        "Modelo de Compressão (0.5B)",
        ["Qwen/Qwen2.5-0.5B", "microsoft/phi-2"],
        index=0
    )
    
    comp_rate = st.slider("Taxa de Compressão Alvo", 1.1, 10.0, 5.0, 0.5)
    
    st.markdown("---")
    if st.button("🗑️ Limpar VRAM/Cache"):
        st.cache_resource.clear()
        cleanup_vram()
        st.success("Memória liberada!")

# --- CABEÇALHO ---
st.title("⚡ LLMLingua: Context Compression Dashboard")
st.markdown("Avalie a eficiência da compressão de prompt em tempo real usando modelos SOTA locais.")

# Inicialização de variáveis no session_state
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🎮 Playground", "📊 Benchmarking", "🧠 Detalhes Técnicos"])

with tab1:
    st.header("Modo Playground")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Entrada de Dados")
        input_type = st.radio("Fonte do Texto:", ["Salmos 91 (Exemplo)", "Texto Customizado"])
        
        if input_type == "Salmos 91 (Exemplo)":
            context_text = get_salmos_text()
        else:
            context_text = st.text_area("Cole seu contexto longo aqui:", height=300)
            
        question = st.text_input("Pergunta ao modelo:", "Resuma as principais promessas deste texto.")
        
        btn_run = st.button("🚀 Executar Inferência")

    with col2:
        st.subheader("Resultados e Visualização")
        if btn_run:
            with st.spinner("Carregando modelos e processando..."):
                monitor = SystemMonitor()
                
                # Carregamento
                llm = load_llm(model_id)
                compressor = load_compressor(compressor_model)
                
                # --- PASSO 1: COMPRESSÃO ---
                st.info("🔄 Comprimindo prompt...")
                monitor.start()
                compressed_dict = compressor.compress(context_text, question, compression_rate=comp_rate)
                comp_time = monitor.stop()["time_seconds"]
                
                # --- PASSO 2: INFERÊNCIA ---
                st.info("🤖 Gerando resposta com prompt comprimido...")
                monitor.start()
                response = llm.generate_response(compressed_dict['compressed_prompt'])
                inf_metrics = monitor.stop()
                
                # Exibição
                st.success("Concluído!")
                
                with st.expander("👁️ Ver Prompt Comprimido (Ilegível para humanos)", expanded=False):
                    st.code(compressed_dict['compressed_prompt'])
                
                st.markdown("#### Resposta do Modelo:")
                st.markdown(f"> {response}")
                
                # Salva métricas para o dashboard
                inf_metrics["time_seconds"] += comp_time
                inf_metrics["cenario"] = f"Comp {comp_rate}x"
                st.session_state.metrics_history.append(inf_metrics)

with tab2:
    st.header("Análise de Performance")
    if not st.session_state.metrics_history:
        st.warning("Execute um teste no Playground para ver as métricas aqui.")
    else:
        df = pd.DataFrame(st.session_state.metrics_history)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        last_run = st.session_state.metrics_history[-1]
        
        m_col1.metric("Tempo Total (s)", f"{last_run['time_seconds']}s")
        m_col2.metric("Pico VRAM (MB)", f"{last_run['vram_peak_mb']}MB")
        m_col3.metric("Uso CPU (%)", f"{last_run['cpu_percent']}%")
        
        st.markdown("---")
        st.subheader("Comparativo Histórico")
        
        fig_vram = px.bar(df, x=df.index, y="vram_peak_mb", color="cenario", title="Pico de VRAM por Execução (MB)")
        st.plotly_chart(fig_vram, use_container_width=True)
        
        fig_time = px.line(df, x=df.index, y="time_seconds", markers=True, title="Latência de Execução (Segundos)")
        st.plotly_chart(fig_time, use_container_width=True)

with tab3:
    st.header("Como funciona?")
    st.markdown("""
    ### 🧬 Teoria da Informação
    A compressão do **LLMLingua** baseia-se na **Perplexidade**. 
    Tokens que são altamente previsíveis em uma frase (como 'o', 'que', 'de') carregam pouca informação semântica e podem ser removidos sem que o modelo principal perca o sentido da mensagem.
    
    ### 🛠️ Stack Tecnológica
    - **Streamlit**: Interface Web.
    - **BitsAndBytes**: Quantização 4-bit para o modelo de 7B.
    - **LLMLingua**: Engine de compressão acelerada.
    - **PyTorch/Transformers**: Backend de inferência.
    
    ### 📈 Benefícios Reais
    1. **Economia de VRAM**: Menos tokens no 'KV Cache' durante a inferência.
    2. **Velocidade**: Redução drástica no tempo de processamento inicial (Pre-fill).
    3. **Contextos Longos**: Permite processar documentos que normalmente excederiam o limite de memória da GPU.
    """)

# --- RODAPÉ ---
st.markdown("---")
st.caption("Desenvolvido para o Experimento de IA - Faculdade 8P | 2026")
