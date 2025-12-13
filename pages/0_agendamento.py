import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import database as db # Conexão com Banco

# Configuração da página
st.set_page_config(page_title="Agendar Horário", page_icon="📅", layout="wide", initial_sidebar_state="collapsed")

# --- LÓGICA DE ESTADO (SESSION STATE) ---
# Garante que o sistema lembre que o agendamento foi feito
if 'sucesso_agendamento' not in st.session_state:
    st.session_state['sucesso_agendamento'] = False

# --- CSS (Tema Azulado / Slate) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stTextInput input {
        background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155 !important; border-radius: 8px;
    }
    div.stButton > button {
        width: 100%; border-radius: 10px; font-weight: 600; border: none; background-color: #3b82f6; color: white !important; height: 3em; transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #2563eb; transform: translateY(-2px); }
    div[data-baseweb="radio"] label { color: #f8fafc !important; background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-right: 10px; margin-bottom: 10px; width: 100%; text-align: center; }
    div[data-baseweb="radio"] label:has(input:checked) { background-color: #3b82f6; border-color: #3b82f6; color: white !important; }
    h1, h2, h3 { color: #f8fafc !important; }
    p, label { color: #cbd5e1 !important; }
    .info-card { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- CARREGA SERVIÇOS DO BANCO ---
try:
    servicos_db = db.listar_servicos()
except AttributeError:
    servicos_db = [] # Fallback se a função não existir ainda

# Fallback se o banco estiver vazio ou der erro
if not servicos_db:
    servicos_db = [{"servico": "Corte Padrão", "preco": 50.00, "duracao": "30 min"}]

st.title("Agendar Horário ✂️")
st.markdown("Reserve seu momento com a gente.")
st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    # 1. Escolha do Serviço
    st.subheader("1. Qual o serviço?")
    opcoes_servicos = {s['servico']: s for s in servicos_db}
    nome_servico = st.selectbox("Selecione o procedimento:", list(opcoes_servicos.keys()))
    servico_selecionado = opcoes_servicos[nome_servico]
    
    st.markdown(f"""
    <div class="info-card">
        <span style="font-size:1.2rem; font-weight:bold;">{nome_servico}</span><br>
        <span style="color:#cbd5e1;">💰 Valor: R$ {servico_selecionado['preco']:.2f} &nbsp;&nbsp;•&nbsp;&nbsp; ⏱️ Duração: {servico_selecionado['duracao']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # 2. Escolha da Data
    st.subheader("2. Qual o dia?")
    agora = datetime.now()
    hoje = agora.date()
    col_data, _ = st.columns([1, 2])
    with col_data:
        data_agendamento = st.date_input("Selecione a data:", min_value=hoje, value=hoje)
    
    st.markdown("---")

    # 3. Escolha do Horário
    st.subheader("3. Qual horário?")
    horarios_possiveis = []
    hora_start = 9
    while hora_start < 19:
        horarios_possiveis.append(f"{hora_start:02d}:00")
        horarios_possiveis.append(f"{hora_start:02d}:30")
        hora_start += 1
    
    if data_agendamento == hoje:
        hora_atual_str = agora.strftime("%H:%M")
        horarios_possiveis = [h for h in horarios_possiveis if h > hora_atual_str]

    # BUSCA NO BANCO OS AGENDAMENTOS DO DIA PARA BLOQUEAR
    data_str = data_agendamento.strftime("%Y-%m-%d")
    try:
        agendamentos_dia = db.listar_agendamentos_por_data(data_str)
        horarios_ocupados = [a['hora'] for a in agendamentos_dia if a['status'] != 'Cancelado']
    except AttributeError:
        horarios_ocupados = [] # Fallback se função não existir
    
    horarios_livres = [h for h in horarios_possiveis if h not in horarios_ocupados]
    
    if not horarios_livres:
        st.warning("😔 Sem horários disponíveis para esta data.")
        horario_escolhido = None
    else:
        horario_escolhido = st.radio("Horários Disponíveis:", horarios_livres, horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")

    # 4. Dados e Salvar
    st.subheader("4. Seus dados")
    nome_cliente = st.text_input("Seu Nome Completo", placeholder="Digite seu nome")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- LÓGICA DE BOTÕES COM SESSION STATE ---
    
    if not st.session_state['sucesso_agendamento']:
        # MOSTRA ESTES BOTÕES APENAS SE AINDA NÃO AGENDOU
        
        col1, col2 = st.columns([1, 1])
        with col1:
             if st.button("⬅️ Cancelar / Voltar", use_container_width=True):
                 st.switch_page("app.py")
        
        with col2:
            confirmar = st.button("✅ Confirmar Agendamento", type="primary", use_container_width=True)

        if confirmar:
            if nome_cliente and horario_escolhido:
                # Cria objeto
                novo_agendamento = {
                    "id": str(uuid.uuid4()),
                    "cliente": nome_cliente,
                    "hora": horario_escolhido,
                    "data": data_str,
                    "servico": servico_selecionado['servico'],
                    "valor_base": servico_selecionado['preco'],
                    "consumo": [],
                    "status": "Aguardando", 
                    "pagamento": None,
                    "criado_em": datetime.now()
                }
                
                # SALVA NO FIREBASE
                try:
                    db.salvar_agendamento(novo_agendamento)
                    
                    # Marca sucesso e recarrega
                    st.session_state['sucesso_agendamento'] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

            else:
                st.warning("⚠️ Preencha nome e horário.")

    else:
        # --- TELA DE SUCESSO ---
        # Botões de confirmar sumiram, agora só aparece o de voltar
        st.success(f"Agendado com sucesso para {data_str} às {horario_escolhido}!")
        st.balloons()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão que limpa o estado e volta
        if st.button("🏠 Voltar ao Início", type="primary", use_container_width=True):
            del st.session_state['sucesso_agendamento']
            st.switch_page("app.py")