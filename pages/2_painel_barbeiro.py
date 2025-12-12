import streamlit as st
import pandas as pd
from datetime import datetime
import database as db # Conexão BD

st.set_page_config(page_title="Painel Barbeiro", page_icon="💈", layout="wide", initial_sidebar_state="collapsed")

# CSS (Mantendo padrão Slate)
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    div.stButton > button { width: 100%; border-radius: 10px; font-weight: 600; border: none; background-color: #3b82f6; color: white !important; height: 3em; transition: all 0.2s; }
    div.stButton > button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .card-cliente { background-color: #1e293b; border: 1px solid #334155; border-left: 5px solid #f59e0b; padding: 20px; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
    .card-pagamento-solicitado { border-left: 5px solid #ec4899; background-color: #334155; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(236, 72, 153, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(236, 72, 153, 0); } 100% { box-shadow: 0 0 0 0 rgba(236, 72, 153, 0); } }
    h1, h2, h3, p, span, b { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("Painel de Controle 💈")

# Navegação
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("💰 Ver Financeiro", use_container_width=True): st.switch_page("pages/3_financeiro.py")
with col_nav2:
    if st.button("⚙️ Cadastros", use_container_width=True): st.switch_page("pages/4_cadastros.py")

st.markdown("---")

# Filtro de Data
col_data, col_filtro = st.columns([1, 2])
with col_data:
    # Por padrão mostra hoje, mas barbeiro pode ver amanhã
    data_painel = st.date_input("Data da Agenda", value=datetime.now())
with col_filtro:
    status_filter = st.radio("Filtro:", ["Todos", "Aguardando", "Em Andamento", "Finalizado"], horizontal=True)

# CARREGA DADOS DO BANCO
data_str = data_painel.strftime("%Y-%m-%d")
agenda_bd = db.listar_agendamentos_por_data(data_str)

# Ordena por horário
agenda_bd.sort(key=lambda x: x['hora'])

if not agenda_bd:
    st.info(f"Nenhum agendamento para {data_painel.strftime('%d/%m/%Y')}.")
else:
    for agendamento in agenda_bd:
        # Filtro Visual
        if status_filter != "Todos" and agendamento['status'] != status_filter:
            continue
            
        css_class = "card-cliente"
        aviso_pagamento = ""
        if agendamento.get("pagamento") == "Solicitado Maquininha":
            css_class += " card-pagamento-solicitado"
            aviso_pagamento = "💳 PEDIU MAQUININHA!"
        
        # Renderiza Card
        with st.container():
            st.markdown(f"""
            <div class="{css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0;">{agendamento['hora']} - {agendamento['cliente']}</h3>
                    <h3 style="color:#ec4899; margin:0;">{aviso_pagamento}</h3>
                </div>
                <p style="margin-top:5px;">Serviço: <b style="color:#3b82f6;">{agendamento['servico']}</b> <span style="font-size:0.8em; color:#888">({agendamento['status']})</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            c_detalhes, c_add_rapido, c_finalizar = st.columns([2, 2, 1])
            
            # Detalhes
            with c_detalhes:
                total = agendamento['valor_base']
                itens_texto = []
                for item in agendamento.get('consumo', []):
                    itens_texto.append(f"{item['item']} (R${item['preco']})")
                    total += item['preco']
                
                if itens_texto:
                    st.caption("Consumo: " + ", ".join(itens_texto))
                st.markdown(f"**Total: R$ {total:.2f}**")

            # Adicionar Itens (Atualiza BD)
            with c_add_rapido:
                if agendamento['status'] != "Finalizado":
                    produtos_extras = db.listar_produtos()
                    if produtos_extras:
                        cols_b = st.columns(3)
                        for idx, prod in enumerate(produtos_extras):
                            with cols_b[idx % 3]:
                                if st.button(f"{prod.get('icone','🍺')}", key=f"add_{agendamento['id']}_{idx}", help=f"Add {prod['item']}"):
                                    agendamento.setdefault('consumo', []).append(prod)
                                    agendamento['status'] = "Em Andamento" # Muda status autom.
                                    db.salvar_agendamento(agendamento)
                                    st.rerun()

            # Finalizar (Atualiza BD)
            with c_finalizar:
                if agendamento['status'] != "Finalizado":
                    if st.button("✅ Concluir", key=f"fin_{agendamento['id']}", type="primary"):
                        agendamento['status'] = "Finalizado"
                        agendamento['pagamento'] = "Pago"
                        db.salvar_agendamento(agendamento)
                        st.success("Finalizado!")
                        st.rerun()
                else:
                    st.success("Encerrado")
                    
            st.markdown("---")

if st.button("⬅️ Voltar"): st.switch_page("app.py")