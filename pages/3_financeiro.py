import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database as db  # IMPORTANTE: Importando o módulo do banco de dados

st.set_page_config(page_title="Financeiro", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    /* Fundo Slate 900 e cor do texto claro */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
    
    .metric-card {
        background-color: #1e293b; /* Slate 800 */
        border: 1px solid #334155; /* Borda Slate */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #4caf50; }
    .metric-label { color: #cbd5e1; font-size: 0.9rem; }

    /* Card de Transação */
    .transaction-card {
        background-color: #1e293b; /* Slate 800 */
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6; /* Azul primário */
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .trans-client { font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-bottom: 5px; }
    .trans-value { font-size: 1.3rem; font-weight: bold; color: #4caf50; }
    .trans-detail { font-size: 0.8rem; color: #94a3b8; }

    /* Botões */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        background-color: #3b82f6;
        color: white !important;
        height: 3em;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }
    
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Função para calcular comissões
def calcular_comissao(item):
    # Garante que valor_base seja float
    valor_base = float(item.get('valor_base', 0))
    comissao_servico = valor_base * 0.50 # 50% para o barbeiro
    
    consumo = item.get('consumo', [])
    if consumo:
        total_extras = sum([float(p.get('preco', 0)) for p in consumo])
        comissao_extras = total_extras * 0.10 # 10% na venda de produtos
    else:
        comissao_extras = 0
    
    return comissao_servico + comissao_extras

st.title("Financeiro & Comissões 💰")

# --- MENU ADMINISTRATIVO ---
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("💈 Ir para Painel (Agenda)", use_container_width=True):
        st.switch_page("pages/2_painel_barbeiro.py")
with col_nav2:
    if st.button("⚙️ Ir para Cadastros", use_container_width=True):
        st.switch_page("pages/4_cadastros.py")

st.markdown("---")

# Placeholder para os Cards (será preenchido depois de calcular)
container_metrics = st.container()

st.markdown("<br>", unsafe_allow_html=True)

# --- FILTROS DE DATA ---
# Definimos as datas primeiro para saber o que buscar no banco
col_filtro, col_cal1, col_cal2 = st.columns([1, 1, 1])

hoje = datetime.now().date()
inicio_filtro = hoje
fim_filtro = hoje

with col_filtro:
    periodo = st.selectbox(
        "📅 Filtro de Período", 
        ["Hoje", "Ontem", "Últimos 7 Dias", "Últimos 15 Dias", "Últimos 30 Dias", "Este Mês", "Personalizado"]
    )

# Lógica de Datas
if periodo == "Hoje":
    inicio_filtro, fim_filtro = hoje, hoje
elif periodo == "Ontem":
    inicio_filtro = hoje - timedelta(days=1)
    fim_filtro = inicio_filtro
elif periodo == "Últimos 7 Dias":
    inicio_filtro = hoje - timedelta(days=7)
    fim_filtro = hoje
elif periodo == "Últimos 15 Dias":
    inicio_filtro = hoje - timedelta(days=15)
    fim_filtro = hoje
elif periodo == "Últimos 30 Dias":
    inicio_filtro = hoje - timedelta(days=30)
    fim_filtro = hoje
elif periodo == "Este Mês":
    inicio_filtro = hoje.replace(day=1)
    fim_filtro = hoje

if periodo == "Personalizado":
    with col_cal1:
        inicio_filtro = st.date_input("Data Inicial", value=hoje)
    with col_cal2:
        fim_filtro = st.date_input("Data Final", value=hoje)
else:
    with col_cal1:
        st.markdown(f"<small style='color:#cbd5e1'>De:</small><br><b>{inicio_filtro.strftime('%d/%m/%Y')}</b>", unsafe_allow_html=True)
    with col_cal2:
        st.markdown(f"<small style='color:#cbd5e1'>Até:</small><br><b>{fim_filtro.strftime('%d/%m/%Y')}</b>", unsafe_allow_html=True)


# --- BUSCA REAL NO BANCO DE DADOS ---
vendas_filtradas = []

# Calcula quantos dias tem no intervalo selecionado
delta_dias = (fim_filtro - inicio_filtro).days + 1

# Loop para buscar dia a dia no banco (garante dados reais)
try:
    with st.spinner('Buscando dados financeiros...'):
        for i in range(delta_dias):
            dia_corrente = inicio_filtro + timedelta(days=i)
            dia_str = dia_corrente.strftime("%Y-%m-%d")
            
            # Busca no banco usando a função existente
            agendamentos_dia = db.listar_agendamentos_por_data(dia_str)
            
            # Filtra apenas os finalizados
            for ag in agendamentos_dia:
                if ag.get('status') == 'Finalizado':
                    # Garante que tem a data no objeto
                    ag['data'] = dia_str
                    vendas_filtradas.append(ag)
except Exception as e:
    st.error(f"Erro ao conectar com banco de dados: {e}")

# --- PROCESSAMENTO DOS DADOS ---
if not vendas_filtradas:
    # Se não tiver vendas, mostra zeros nos cards
    with container_metrics:
        c1, c2, c3 = st.columns(3)
        c1.markdown('<div class="metric-card"><div class="metric-label">Faturamento</div><div class="metric-value">R$ 0,00</div></div>', unsafe_allow_html=True)
        c2.markdown('<div class="metric-card"><div class="metric-label">A Pagar</div><div class="metric-value" style="color:#ff9800">R$ 0,00</div></div>', unsafe_allow_html=True)
        c3.markdown('<div class="metric-card"><div class="metric-label">Lucro Líquido</div><div class="metric-value" style="color:#2196f3">R$ 0,00</div></div>', unsafe_allow_html=True)
    
    st.info(f"Nenhuma venda finalizada encontrada entre {inicio_filtro.strftime('%d/%m/%Y')} e {fim_filtro.strftime('%d/%m/%Y')}")
    st.stop()

# Cálculos Finais
dados_fin = []
total_bruto = 0.0
total_comissao = 0.0

for v in vendas_filtradas:
    valor_servico = float(v.get('valor_base', 0))
    
    consumo = v.get('consumo', [])
    if consumo:
        valor_extras = sum([float(p.get('preco', 0)) for p in consumo])
    else:
        valor_extras = 0.0
        
    total_venda = valor_servico + valor_extras
    
    comissao = calcular_comissao(v)
    lucro_loja = total_venda - comissao
    
    total_bruto += total_venda
    total_comissao += comissao
    
    dados_fin.append({
        "Data": v.get("data", str(hoje)),
        "Barbeiro": "Barbeiro", 
        "Cliente": v.get('cliente', 'Desconhecido'),
        "Serviço": v.get('servico', 'Serviço'),
        "Total Venda": total_venda,
        "Comissão": comissao,
        "Loja": lucro_loja,
        "Pagamento": v.get('pagamento', 'N/D')
    })

df_fin = pd.DataFrame(dados_fin)
lucro_liquido = total_bruto - total_comissao

# --- PREENCHENDO O TOPO (CARDS) ---
with container_metrics:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Faturamento</div>
            <div class="metric-value">R$ {total_bruto:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">A Pagar (Comissões)</div>
            <div class="metric-value" style="color:#ff9800">R$ {total_comissao:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Lucro Líquido</div>
            <div class="metric-value" style="color:#2196f3">R$ {lucro_liquido:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- EXTRATO DETALHADO ---
st.subheader(f"Extrato Detalhado ({len(vendas_filtradas)} Vendas)")

# Ordena os dados por data
if not df_fin.empty:
    df_fin['Data_Sort'] = pd.to_datetime(df_fin['Data'], format='%Y-%m-%d', errors='coerce')
    df_fin = df_fin.sort_values(by='Data_Sort', ascending=False)

    for index, row in df_fin.iterrows():
        total_display = f"R$ {row['Total Venda']:.2f}"
        comissao_display = f"R$ {row['Comissão']:.2f}"
        lucro_display = f"R$ {row['Loja']:.2f}"
        
        try:
            data_formatada = datetime.strptime(str(row['Data']), '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            data_formatada = str(row['Data'])
        
        st.markdown(f"""
    <div class="transaction-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="trans-client">{row['Cliente']}</span>
            <span class="trans-value">{total_display}</span>
        </div>
        <div style="margin-top:5px; padding-top:5px; border-top:1px solid #334155;">
            <p class="trans-detail" style="margin-bottom:2px;">
                Serviço: <b style="color:#3b82f6 !important;">{row['Serviço']}</b>
            </p>
            <p class="trans-detail" style="margin-bottom:2px;">
                Data: {data_formatada} • Pagamento: {row['Pagamento']}
            </p>
            <p class="trans-detail">
                Comissão: <span style="color:#ff9800;">{comissao_display}</span> | Lucro da Casa: <span style="color:#2196f3;">{lucro_display}</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")

# --- GRÁFICO ---
if not df_fin.empty:
    if (fim_filtro - inicio_filtro).days > 1:
        fig = px.bar(df_fin, x='Data', y='Total Venda', title="Faturamento por Dia", template='plotly_dark')
    else:
        fig = px.bar(df_fin, x='Cliente', y=['Loja', 'Comissão'], title="Divisão por Atendimento", barmode='stack', template='plotly_dark')
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

# Botão Voltar
st.markdown("<br>", unsafe_allow_html=True)
if st.button("⬅️ Voltar para Home"):
    st.switch_page("app.py")