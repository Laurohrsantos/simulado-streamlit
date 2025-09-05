import streamlit as st
from utils.auth import require_auth

# Protege a página
require_auth()

st.title(f"Bem-vindo, {st.session_state['name']}!")
st.write("Selecione uma opção no menu à esquerda para começar os seus estudos ou analisar o seu progresso.")
st.info("Esta é a sua página inicial. Novidades e avisos poderão aparecer aqui no futuro.")
