import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="BarberManager", page_icon="✂️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILIZAÇÃO CSS (Tema Azulado / Slate - Estilo Igreja) ---
st.markdown("""
<style>
    /* Ocultar Sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    /* Fundo Global Azul Noturno (Slate 900) */
    .stApp {
        background-color: #0f172a !important; 
        color: #f8fafc !important;
    }
    
    /* Card da Home (Slate 800) */
    .section-card {
        background-color: #1e293b;
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid #334155; /* Borda sutil */
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Efeito Hover no Card */
    .section-card:hover {
        transform: translateY(-5px);
        border-color: #3b82f6; /* Azul Vibrante ao passar o mouse */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        background-color: #334155;
    }
    
    /* Tipografia */
    h1 { font-size: 3.5rem; margin: 0; } /* Ícones maiores */
    h3 { color: #f8fafc; margin: 15px 0; font-weight: 600; }
    p { color: #cbd5e1; margin: 0; font-size: 1rem; }
    
    /* Estilização dos Botões (Azul Vibrante) */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        background-color: #3b82f6;
        color: white !important;
        height: 3em;
        margin-top: 15px;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2563eb; /* Azul um pouco mais escuro no hover */
        transform: scale(1.02);
    }
    
    /* Ajuste de Títulos da Página */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DE DADOS
if "agenda_hoje" not in st.session_state:
    st.session_state.agenda_hoje = [
        {"id": 1, "cliente": "João Silva", "hora": "14:00", "servico": "Corte Clássico", "valor_base": 50.00, "consumo": [], "status": "Em Andamento", "pagamento": None, "data": datetime.now().strftime("%Y-%m-%d")},
        {"id": 2, "cliente": "Pedro Costa", "hora": "14:45", "servico": "Barba Terapia", "valor_base": 40.00, "consumo": [], "status": "Aguardando", "pagamento": None, "data": datetime.now().strftime("%Y-%m-%d")},
    ]

if "catalogo_extras" not in st.session_state:
    st.session_state.catalogo_extras = [
        {"item": "Cerveja Heineken", "preco": 12.00, "icone": "🍺"},
        {"item": "Refrigerante", "preco": 6.00, "icone": "🥤"},
        {"item": "Pomada Modeladora", "preco": 35.00, "icone": "🧴"},
        {"item": "Acabamento Sobrancelha", "preco": 15.00, "icone": "🤨"},
    ]

if "catalogo_servicos" not in st.session_state:
    st.session_state.catalogo_servicos = [
        {"servico": "Corte Cabelo", "preco": 50.00, "duracao": "30 min"},
        {"servico": "Barba", "preco": 40.00, "duracao": "30 min"},
        {"servico": "Corte + Barba", "preco": 80.00, "duracao": "60 min"},
    ]

# --- TELA INICIAL ---
st.title("BarberManager ✂️")
st.markdown("Bem-vindo! Identifique-se para começar.")

st.markdown("<br>", unsafe_allow_html=True) # Espaçamento extra

col_cli, col_barb = st.columns(2, gap="large")

# COLUNA 1: ÁREA DO CLIENTE (Unificada)
with col_cli:
    st.markdown("""
    <div class="section-card">
        <h1>👤</h1>
        <h3>Sou Cliente</h3>
        <p>Agendar horário ou pagar conta</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Área do Cliente", use_container_width=True):
        st.switch_page("pages/1_comanda_digital.py")

# COLUNA 2: ÁREA DO BARBEIRO
with col_barb:
    st.markdown("""
    <div class="section-card">
        <h1>💈</h1>
        <h3>Sou Barbeiro</h3>
        <p>Gestão, Agenda e Financeiro</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Painel Administrativo", use_container_width=True):
        st.switch_page("pages/2_painel_barbeiro.py")