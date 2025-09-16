import streamlit as st
from database.db_handler import get_user
from passlib.context import CryptContext
import datetime

# --- CONFIGURAÇÃO DE CRIPTOGRAFIA ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica uma senha em texto plano contra um hash."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    """Gera um hash para uma nova senha."""
    return pwd_context.hash(password)

def login(username, password):
    """
    Tenta autenticar um utilizador, verificando a senha e a data de expiração do acesso.
    """
    user_data = get_user(username)
    if not user_data:
        return False, "Utilizador ou senha incorretos."

    if not verify_password(password, user_data.get('password_hash', '')):
        return False, "Utilizador ou senha incorretos."

    expiry_date_str = user_data.get('access_expires_on')
    if expiry_date_str:
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        if datetime.date.today() > expiry_date:
            return False, "O seu acesso a esta plataforma expirou."

    st.session_state['authenticated'] = True
    st.session_state['username'] = username
    st.session_state['role'] = user_data['role']
    st.session_state['name'] = user_data.get('name', username)
    st.session_state['access_expires_on'] = user_data.get('access_expires_on')
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

