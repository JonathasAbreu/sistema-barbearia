import streamlit as st
import pandas as pd
import database as db  # Importamos nosso módulo de banco de dados

st.set_page_config(page_title="Cadastros", page_icon="⚙️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILIZAÇÃO CSS (Tema Azulado / Slate) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    
    /* Fundo Global Azul Noturno (Slate 900) */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    
    /* Botões de Navegação (Topo) */
    div.stButton > button {
        width: 100%; border-radius: 10px; font-weight: 600; border: none;
        background-color: #3b82f6; color: white !important; height: 3em; transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #2563eb; transform: translateY(-2px); }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important; color: #f8fafc !important;
        border: 1px solid #334155 !important; border-radius: 8px;
    }
    
    /* Headers */
    .section-header {
        margin-top: 30px; margin-bottom: 15px; padding-bottom: 10px;
        border-bottom: 1px solid #334155; color: #3b82f6; font-size: 1.4rem; font-weight: 600;
    }

    /* Tabela Customizada */
    .list-cell-start {
        background-color: #1e293b; padding: 12px; border-top: 1px solid #334155; border-bottom: 1px solid #334155;
        border-left: 5px solid #3b82f6; border-top-left-radius: 8px; border-bottom-left-radius: 8px;
        height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
    }
    .list-cell {
        background-color: #1e293b; padding: 12px; border-top: 1px solid #334155; border-bottom: 1px solid #334155;
        height: 100%; display: flex; align-items: center; color: #f8fafc;
    }
    .list-header {
        font-weight: bold; color: #94a3b8; padding-bottom: 10px; margin-bottom: 10px; font-size: 0.9rem; text-transform: uppercase;
    }
    
    /* Texto Global */
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("Configurações e Cadastros ⚙️")

# Navegação
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("💈 Ir para Painel (Agenda)", use_container_width=True): st.switch_page("pages/2_painel_barbeiro.py")
with col_nav2:
    if st.button("💰 Ir para Financeiro", use_container_width=True): st.switch_page("pages/3_financeiro.py")

st.markdown("---")

tab1, tab2 = st.tabs(["🛒 Produtos (Bar/Loja)", "✂️ Serviços e Preços"])

# ==================== ABA 1: PRODUTOS ====================
with tab1:
    st.markdown('<div class="section-header">Novo Produto</div>', unsafe_allow_html=True)
    
    # Formulário Salva direto no Banco
    with st.form("add_prod", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
        with c1: icone = st.text_input("Ícone", value="🍺")
        with c2: nome = st.text_input("Nome", placeholder="Ex: Cerveja IPA")
        with c3: preco = st.number_input("Preço (R$)", min_value=0.0, step=1.0)
        with c4:
            st.write("")
            st.write("")
            if st.form_submit_button("➕ Salvar"):
                if nome:
                    # SALVA NO BANCO
                    db.salvar_produto({"item": nome, "preco": preco, "icone": icone})
                    st.success("Salvo!")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # LISTA (LÊ DO BANCO)
    produtos_db = db.listar_produtos()
    
    if produtos_db:
        st.markdown('<div class="section-header">Produtos Cadastrados</div>', unsafe_allow_html=True)
        
        # Cabeçalho
        c_h1, c_h2, c_h3, c_h4 = st.columns([1, 3, 2, 1])
        c_h1.markdown('<div class="list-header">ÍCONE</div>', unsafe_allow_html=True)
        c_h2.markdown('<div class="list-header">NOME</div>', unsafe_allow_html=True)
        c_h3.markdown('<div class="list-header">PREÇO</div>', unsafe_allow_html=True)
        c_h4.markdown('<div class="list-header" style="text-align:center">AÇÃO</div>', unsafe_allow_html=True)

        # Loop
        for prod in produtos_db:
            c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
            with c1: st.markdown(f'<div class="list-cell-start">{prod.get("icone", "📦")}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="list-cell"><b>{prod["item"]}</b></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="list-cell" style="color:#4caf50;">R$ {prod["preco"]:.2f}</div>', unsafe_allow_html=True)
            with c4:
                with st.container():
                    st.markdown('<div style="height: 5px"></div>', unsafe_allow_html=True)
                    # DELETE NO BANCO
                    if st.button("🗑️", key=f"del_prod_{prod['item']}", use_container_width=True):
                        db.deletar_produto(prod['item'])
                        st.rerun()
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum produto encontrado no banco de dados.")

# ==================== ABA 2: SERVIÇOS ====================
with tab2:
    st.markdown('<div class="section-header">Tabela de Serviços</div>', unsafe_allow_html=True)
    
    with st.form("add_serv", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1: nome_serv = st.text_input("Serviço", placeholder="Ex: Platinado")
        with c2: preco_serv = st.number_input("Preço (R$)", min_value=0.0, step=5.0)
        with c3: duracao_serv = st.selectbox("Duração", ["15 min", "30 min", "45 min", "60 min", "90 min"])
        with c4:
            st.write("")
            st.write("")
            if st.form_submit_button("➕ Salvar"):
                if nome_serv:
                    # SALVA NO BANCO
                    db.salvar_servico({"servico": nome_serv, "preco": preco_serv, "duracao": duracao_serv})
                    st.success("Salvo!")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # LISTA (LÊ DO BANCO)
    servicos_db = db.listar_servicos()

    if servicos_db:
        st.markdown('<div class="section-header">Serviços Ativos</div>', unsafe_allow_html=True)

        c_s1, c_s2, c_s3, c_s4 = st.columns([3, 2, 2, 1])
        c_s1.markdown('<div class="list-header">SERVIÇO</div>', unsafe_allow_html=True)
        c_s2.markdown('<div class="list-header">PREÇO</div>', unsafe_allow_html=True)
        c_s3.markdown('<div class="list-header">DURAÇÃO</div>', unsafe_allow_html=True)
        c_s4.markdown('<div class="list-header" style="text-align:center">AÇÃO</div>', unsafe_allow_html=True)

        for serv in servicos_db:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1: st.markdown(f'<div class="list-cell-start"><b>{serv["servico"]}</b></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="list-cell" style="color:#4caf50;">R$ {serv["preco"]:.2f}</div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="list-cell" style="color:#94a3b8;">{serv["duracao"]}</div>', unsafe_allow_html=True)
            with c4:
                with st.container():
                    st.markdown('<div style="height: 5px"></div>', unsafe_allow_html=True)
                    # DELETE NO BANCO
                    if st.button("🗑️", key=f"del_serv_{serv['servico']}", use_container_width=True):
                        db.deletar_servico(serv['servico'])
                        st.rerun()
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum serviço encontrado no banco de dados.")

st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("⬅️ Voltar para Home"): st.switch_page("app.py")