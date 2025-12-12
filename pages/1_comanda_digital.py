import streamlit as st
import pandas as pd
import time
import unicodedata
from datetime import datetime
import database as db

st.set_page_config(page_title="Área do Cliente", page_icon="👤", layout="wide", initial_sidebar_state="collapsed")

def normalizar_texto(texto):
    if not texto: return ""
    nfkd = unicodedata.normalize('NFD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# CSS (Padrão Slate)
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    .stTextInput input { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155 !important; border-radius: 8px; }
    .menu-btn { padding: 30px; background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; text-align: center; margin-bottom: 20px; transition: transform 0.2s; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
    .menu-btn:hover { transform: translateY(-5px); border-color: #3b82f6; }
    .total-card { background-color: #059669; color: white; padding: 20px; border-radius: 15px; text-align: center; font-size: 1.5rem; font-weight: bold; margin-top: 20px; }
    div.stButton > button { width: 100%; border-radius: 10px; font-weight: 600; border: none; background-color: #3b82f6; color: white !important; height: 3em; transition: all 0.2s; }
    div.stButton > button:hover { background-color: #2563eb; transform: translateY(-2px); }
    h1, h2, h3, p, label { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

if "cliente_id_logado" not in st.session_state:
    st.session_state.cliente_id_logado = None

# FASE 1: LOGIN / BUSCA
if st.session_state.cliente_id_logado is None:
    st.title("Olá! O que deseja fazer?")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    
    with c1:
        st.markdown('<div class="menu-btn"><h2 style="font-size:3rem;">🔎</h2><h3>Já agendei / Check-in</h3><p>Vim cortar o cabelo agora</p></div>', unsafe_allow_html=True)
        with st.expander("👉 Buscar meu nome", expanded=True):
            nome_busca = st.text_input("Digite seu nome:", key="busca_nome_input")
            if st.button("Acessar Comanda", type="primary", use_container_width=True):
                if nome_busca:
                    # Busca no banco usando a função auxiliar
                    encontrados = db.buscar_agendamento_por_nome(nome_busca)
                    
                    if not encontrados:
                        st.error("Agendamento ativo não encontrado.")
                    elif len(encontrados) == 1:
                        st.session_state.cliente_id_logado = encontrados[0]['id']
                        st.rerun()
                    else:
                        st.warning("Encontrei mais de um. Digite o sobrenome.")

    with c2:
        st.markdown('<div class="menu-btn"><h2 style="font-size:3rem;">📅</h2><h3>Quero Agendar</h3><p>Marcar um horário</p></div>', unsafe_allow_html=True)
        st.write(""); st.write(""); st.write("")
        if st.button("📅 Reservar Horário", use_container_width=True):
            st.switch_page("pages/0_agendamento.py")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("⬅️ Voltar"): st.switch_page("app.py")
    st.stop()

# FASE 2: COMANDA (DADOS VINDOS DO BANCO)
# Precisamos buscar o agendamento atualizado do banco a cada refresh
agendamentos_todos = db.listar_agendamentos_todos() # Otimização: poderia buscar por ID direto se tivesse função, mas listar todos funciona para poucos dados
agendamento = next((a for a in agendamentos_todos if a['id'] == st.session_state.cliente_id_logado), None)

if not agendamento or agendamento['status'] == 'Finalizado':
    st.session_state.cliente_id_logado = None
    st.warning("Atendimento finalizado ou não encontrado.")
    if st.button("Voltar"): st.rerun()
    st.stop()

# Layout Comanda
c_head1, c_head2 = st.columns([3, 1])
with c_head1: st.markdown(f"### Olá, {agendamento['cliente']}!")
with c_head2: 
    if st.button("Sair"): 
        st.session_state.cliente_id_logado = None
        st.rerun()

st.markdown("---")
col_resumo, col_adicionais = st.columns([1, 1], gap="large")

with col_resumo:
    st.markdown("### 🧾 Consumo Atual")
    try:
        data_fmt = datetime.strptime(agendamento.get('data'), '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        data_fmt = "Hoje"

    st.markdown(f"""
    <div style="background-color:#1e293b; padding:15px; border-radius:10px; border:1px solid #334155;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #334155; padding-bottom:10px;">
             <span style="color:#cbd5e1;">📅 {data_fmt}</span>
             <span style="color:#cbd5e1; font-weight:bold;">⏰ {agendamento['hora']}</span>
        </div>
        <p style="margin:0; font-weight:bold; font-size:1.1rem; color:#f8fafc;">{agendamento['servico']}</p>
        <p style="margin:0; color:#3b82f6;">R$ {agendamento['valor_base']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_extras = 0
    if agendamento.get('consumo'):
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Itens Adicionados:")
        for i, item in enumerate(agendamento['consumo']):
            c_nome, c_val, c_del = st.columns([3, 2, 1])
            with c_nome: st.write(f"+ {item['item']}")
            with c_val: st.write(f"R$ {item['preco']:.2f}")
            with c_del:
                if st.button("🗑️", key=f"del_{i}"):
                    agendamento['consumo'].pop(i)
                    db.salvar_agendamento(agendamento) # Salva remoção no banco
                    st.rerun()
            total_extras += item['preco']
        
    total_geral = agendamento['valor_base'] + total_extras
    st.markdown(f'<div class="total-card">Total: R$ {total_geral:.2f}</div>', unsafe_allow_html=True)
    
    if agendamento.get("pagamento") == "Solicitado Maquininha":
        st.warning("⏳ Aguardando maquininha...")
    elif agendamento.get("pagamento") == "Pago":
        st.success("✅ Conta Paga!")

with col_adicionais:
    st.markdown("### ➕ Adicionar")
    produtos_extras = db.listar_produtos()
    if produtos_extras:
        for produto in produtos_extras:
            if st.button(f"{produto.get('icone','📦')} {produto['item']} - R$ {produto['preco']:.0f}", key=f"add_{produto['item']}"):
                agendamento.setdefault('consumo', []).append(produto)
                db.salvar_agendamento(agendamento) # Salva adição no banco
                st.toast("Adicionado!", icon="✅")
                time.sleep(0.5)
                st.rerun()

st.markdown("---")
if agendamento.get("status") != "Finalizado" and agendamento.get("pagamento") != "Pago":
    st.subheader("💳 Pagar")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💠 PIX", type="primary", use_container_width=True): st.info("Chave PIX: (QR Code aqui)")
    with c2:
        if st.button("💳 Maquininha", use_container_width=True):
            agendamento['pagamento'] = "Solicitado Maquininha"
            db.salvar_agendamento(agendamento)
            st.rerun()  