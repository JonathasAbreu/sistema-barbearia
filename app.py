import streamlit as st
import time

# Configuração da Página
st.set_page_config(
    page_title="Barbearia Vip", 
    page_icon="✂️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    /* Esconde menu padrão */
    [data-testid="stSidebar"] { display: none; }
    
    /* Fundo e cores gerais */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    
    /* Estilo dos Cards de Seleção */
    .card-home {
        background-color: #1e293b; /* Slate 800 */
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 250px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .card-home:hover {
        transform: translateY(-5px);
        border-color: #3b82f6; /* Azul destaque */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .icon-home { font-size: 4rem; margin-bottom: 15px; }
    .title-home { font-size: 1.8rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px; }
    .desc-home { font-size: 0.95rem; color: #94a3b8; }

    /* Estilo dos Botões */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        background-color: #3b82f6;
        color: white !important;
        height: 3.5em;
        margin-top: 10px;
        font-size: 1rem;
        transition: background-color 0.2s;
    }
    div.stButton > button:hover { background-color: #2563eb; }
    
    /* Input Style para Login */
    .stTextInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESSÃO (Controle de telas) ---
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

# --- LÓGICA DE LOGIN ---
def verificar_login():
    email = st.session_state.email_input
    senha = st.session_state.senha_input
    
    if email == "gustavodocorte@salao.com" and senha == "123":
        st.success("Login realizado com sucesso! Redirecionando...")
        st.session_state['admin_logado'] = True
        time.sleep(1) # Pequena pausa para ver a mensagem
        st.switch_page("pages/2_painel_barbeiro.py")
    else:
        st.error("E-mail ou senha incorretos.")

# --- INTERFACE ---

st.title("Gustavo Do Corte ✂️")

# Se o botão de login foi clicado, mostra o formulário
if st.session_state.show_login:
    st.markdown("### 🔒 Acesso Restrito ao Barbeiro")
    st.write("Insira suas credenciais para gerenciar o salão.")
    
    col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
    
    with col_login2:
        st.text_input("E-mail", key="email_input", placeholder="admin@salao.com.br")
        st.text_input("Senha", type="password", key="senha_input", placeholder="••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Entrar no Sistema"):
            verificar_login()
            
        if st.button("⬅️ Voltar", type="secondary"):
            st.session_state.show_login = False
            st.rerun()

# Se não, mostra a tela inicial padrão (Cards)
else:
    st.write("Bem-vindo! Identifique-se para começar.")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Card Cliente
        st.markdown("""
        <div class="card-home">
            <div class="icon-home">👤</div>
            <div class="title-home">Sou Cliente</div>
            <div class="desc-home">Agende ou consulte seus horários</div> 
        </div>
        """, unsafe_allow_html=True)
            
        if st.button("📄 Consultar Agendamento / Agendar", use_container_width=True):
            st.switch_page("pages/1_comanda_digital.py")

    with col2:
        # Card Barbeiro
        st.markdown("""
        <div class="card-home">
            <div class="icon-home">💈</div>
            <div class="title-home">Sou Barbeiro</div>
            <div class="desc-home">Gestão, Agenda e Financeiro</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ao clicar aqui, ativamos o modo Login
        if st.button("Acessar Painel Administrativo", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()