import streamlit as st
from database.db_handler import get_user
from passlib.context import CryptContext
from passlib.hash import bcrypt
import datetime

# --- CONFIGURAÇÃO DE CRIPTOGRAFIA ---
# Usamos passlib para uma gestão de senhas segura
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    normalized_hash = bcrypt.normhash(hashed_password)
    return pwd_context.verify(plain_password, normalized_hash)

def login(username, password):
    """
    Tenta autenticar um utilizador, verificando a senha e a data de expiração do acesso.
    """
    user_data = get_user(username)
    if not user_data:
        return False, "Usuário ou senha incorretos."

    # 1. Verifica a senha
    if not verify_password(password, user_data.get('password_hash', '')):
        return False, "Usuário ou senha incorretos."

    # 2. Verifica a data de expiração do acesso
    expiry_date_str = user_data.get('access_expires_on')
    if expiry_date_str:
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        if datetime.date.today() > expiry_date:
            return False, "O seu acesso a esta plataforma expirou."

    # Se tudo estiver correto, armazena os dados na sessão
    st.session_state['authenticated'] = True
    st.session_state['username'] = username
    st.session_state['role'] = user_data['role']
    st.session_state['name'] = user_data.get('name', username)
    st.session_state['access_expires_on'] = user_data['access_expires_on']
    return True, "Login bem-sucedido!"

def logout():
    """Limpa a sessão para terminar o login do utilizador."""
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]
    
def is_authenticated():
    """Verifica se há um utilizador autenticado na sessão."""
    return st.session_state.get('authenticated', False)

def get_user_role():
    """Devolve o papel (role) do utilizador com sessão iniciada."""
    return st.session_state.get('role')

def require_auth():
    """
    Função de guarda para páginas protegidas. Verifica a autenticação em cada carregamento.
    """
    if not is_authenticated():
        st.error("Precisa de ter uma sessão iniciada para aceder a esta página.")
        st.info("Por favor, retorne à página principal para fazer o login.")
        st.stop()

