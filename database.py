import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os # Necessário para verificar se o arquivo existe

# --- CONFIGURAÇÃO DA CONEXÃO ---
def init_firestore():
    """Conecta ao Firestore (Local ou Nuvem)"""
    # Verifica se já existe uma conexão ativa para não inicializar duas vezes
    if not firebase_admin._apps:
        try:
            # 1. PRIORIDADE TOTAL: Arquivo Local (Desenvolvimento)
            # Verifica explicitamente se o arquivo json existe na pasta
            if os.path.exists("firestore_key.json"):
                cred = credentials.Certificate("firestore_key.json")
                firebase_admin.initialize_app(cred)
            
            # 2. Fallback: Streamlit Cloud Secrets (Apenas se não tiver arquivo local)
            # Isso evita o erro "No secrets found" quando rodando localmente
            elif hasattr(st, "secrets") and "firebase" in st.secrets:
                key_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred)
                
            else:
                st.error("⚠️ ERRO CRÍTICO: Nenhuma chave de acesso encontrada!")
                st.info("Certifique-se que o arquivo 'firestore_key.json' está na pasta do projeto.")
                return None
            
        except Exception as e:
            st.error(f"Erro ao conectar no Banco de Dados: {e}")
            return None

    return firestore.client()

# ================= PRODUTOS =================
def salvar_produto(produto):
    db = init_firestore()
    if db: db.collection("produtos").document(produto['item']).set(produto)

def listar_produtos():
    db = init_firestore()
    if not db: return []
    return [doc.to_dict() for doc in db.collection("produtos").stream()]

def deletar_produto(nome_item):
    db = init_firestore()
    if db: db.collection("produtos").document(nome_item).delete()

# ================= SERVIÇOS =================
def salvar_servico(servico):
    db = init_firestore()
    if db: db.collection("servicos").document(servico['servico']).set(servico)

def listar_servicos():
    db = init_firestore()
    if not db: return []
    return [doc.to_dict() for doc in db.collection("servicos").stream()]

def deletar_servico(nome_servico):
    db = init_firestore()
    if db: db.collection("servicos").document(nome_servico).delete()

# ================= AGENDAMENTOS =================
def salvar_agendamento(agendamento):
    """Salva um novo agendamento ou atualiza existente"""
    db = init_firestore()
    if db:
        # Usa o ID único (uuid) como chave do documento
        db.collection("agendamentos").document(agendamento['id']).set(agendamento)

def listar_agendamentos_todos():
    """Retorna todos os agendamentos (para histórico/financeiro)"""
    db = init_firestore()
    if not db: return []
    return [doc.to_dict() for doc in db.collection("agendamentos").stream()]

def listar_agendamentos_por_data(data_str):
    """Retorna agendamentos de um dia específico"""
    db = init_firestore()
    if not db: return []
    
    # Filtra no banco onde o campo 'data' é igual a data_str
    docs = db.collection("agendamentos").where("data", "==", data_str).stream()
    return [doc.to_dict() for doc in docs]

def buscar_agendamento_por_nome(nome_parcial):
    """Busca agendamentos ativos pelo nome do cliente"""
    db = init_firestore()
    if not db: return []
    
    todos = listar_agendamentos_todos()
    
    resultados = []
    nome_busca = nome_parcial.lower()
    
    for a in todos:
        if a.get('status') != 'Finalizado' and nome_busca in a.get('cliente', '').lower():
            resultados.append(a)
            
    return resultados