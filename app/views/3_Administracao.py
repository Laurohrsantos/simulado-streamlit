import streamlit as st
from utils.auth import require_role
from pathlib import Path
from database.db_handler import get_all_question_banks, get_all_users, update_user_simulations


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Administração")
# Protege a página e exige o papel de 'admin'
require_role('admin')


st.title("Painel de Administração")

# --- SECÇÃO DE GESTÃO DE BANCOS DE QUESTÕES ---
with st.container(border=True):
    st.subheader("Gestão de Bancos de Questões")
    DATA_DIR = Path(__file__).parent.parent / "data"
    DATA_DIR.mkdir(exist_ok=True)

    st.write("Faça upload de novos bancos de questões em formato JSON.")
    uploaded_files = st.file_uploader(
        "Selecione um ou mais ficheiros JSON",
        type="json",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                with open(DATA_DIR / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Ficheiro '{uploaded_file.name}' carregado!")
            except Exception as e:
                st.error(f"Erro ao guardar '{uploaded_file.name}': {e}")
        # Limpa o uploader após o sucesso para evitar re-upload
        st.rerun()


    st.write("**Bancos de Questões Atuais:**")
    current_banks = get_all_question_banks()
    if not current_banks:
        st.warning("Nenhum banco de questões encontrado na pasta 'data'.")
    else:
        st.info(f"Encontrados {len(current_banks)} bancos: {', '.join(f'`{b}`' for b in current_banks)}")


# --- SECÇÃO DE ATRIBUIÇÃO DE ACESSO ---
with st.container(border=True):
    st.subheader("Atribuir Acesso a Simulados")
    
    all_users = get_all_users()
    all_banks = get_all_question_banks()
    
    # Remove o admin da lista de utilizadores a serem geridos
    users_to_manage = {name: data for name, data in all_users.items() if data['role'] != 'admin'}

    if not users_to_manage:
        st.info("Nenhum utilizador padrão encontrado para gerir.")
    elif not all_banks:
        st.warning("Nenhum banco de questões disponível para ser atribuído.")
    else:
        with st.form("permissions_form"):
            for username, user_data in users_to_manage.items():
                st.write(f"**Utilizador:** {user_data.get('name', username)}")
                
                # O valor padrão são as simulações que o utilizador já possui
                current_simulations = user_data.get('available_simulations', [])
                
                selected_simulations = st.multiselect(
                    f"Selecione os simulados para {user_data.get('name', username)}:",
                    options=all_banks,
                    default=current_simulations,
                    key=f"sims_{username}"
                )
            
            submitted = st.form_submit_button("Guardar Permissões")
            if submitted:
                for username in users_to_manage.keys():
                    # Obtém as seleções do formulário para cada utilizador
                    new_simulations = st.session_state[f"sims_{username}"]
                    update_user_simulations(username, new_simulations)
                st.success("Permissões atualizadas com sucesso!")

