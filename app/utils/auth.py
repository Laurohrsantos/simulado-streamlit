import streamlit as st
from database.db_handler import get_user

def login(username, password):
    """
    Tenta autenticar um utilizador.
    Se bem-sucedido, armazena informações do utilizador na sessão.
    """
    user_data = get_user(username)
    if user_data and user_data['password'] == password:
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.session_state['role'] = user_data['role']
        st.session_state['name'] = user_data.get('name', username)
        return True
    return False

def logout():
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]
    

def is_authenticated():
    """Verifica se há um utilizador autenticado na sessão."""
    return st.session_state.get('authenticated', False)

def get_user_role():
    """Devolve o papel (role) do utilizador com sessão iniciada."""
    return st.session_state.get('role')

def require_auth(redirect_to_login=True):
    """
    Função de guarda para páginas protegidas.
    """
    if not is_authenticated():
        if redirect_to_login:
            st.title("Acesso Negado")
            st.error("Precisa de ter uma sessão iniciada para aceder a esta página.")
            st.info("Por favor, retorne à página principal para fazer o login.")
        st.stop()

def require_role(role):
    """
    Função de guarda para páginas com acesso restrito por papel.
    """
    require_auth()
    if get_user_role() != role:
        st.title("Permissão Negada")
        st.error("Não tem permissão para aceder a esta página.")
        st.stop()

