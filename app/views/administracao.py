import streamlit as st
from pathlib import Path
from database.db_handler import (get_all_question_banks, get_all_users, update_user_simulations, 
                                 update_user_expiry, add_user, username_exists, save_global_message)
from utils.auth import hash_password
import datetime

def render_page():
    """Renderiza o painel de administração completo."""
    st.title("Painel de Administração")

    tab1, tab2, tab3, tab4 = st.tabs(["Gerir Utilizadores", "Cadastrar Utilizador", "Gerir Bancos", "Enviar Mensagem"])

    with tab1:
        st.subheader("Gerir Acesso dos Utilizadores")
        all_users = get_all_users()
        all_banks = get_all_question_banks()
        users_to_manage = {name: data for name, data in all_users.items() if data['role'] != 'admin'}

        if not users_to_manage:
            st.info("Nenhum utilizador padrão encontrado para gerir.")
        else:
            for username, user_data in users_to_manage.items():
                with st.expander(f"Gerir: **{user_data.get('name', username)}** ({username})"):
                    # Validade do Acesso
                    current_expiry_str = user_data.get('access_expires_on')
                    current_expiry_date = datetime.datetime.strptime(current_expiry_str, "%Y-%m-%d").date() if current_expiry_str else None
                    new_expiry_date = st.date_input("Validade do acesso:", value=current_expiry_date, min_value=datetime.date.today(), key=f"date_{username}")
                    
                    # Simulados Disponíveis
                    current_simulations = user_data.get('available_simulations', [])
                    selected_simulations = st.multiselect("Simulados disponíveis:", options=all_banks, default=current_simulations, key=f"sims_{username}")
                    
                    if st.button("Guardar Alterações", key=f"save_{username}"):
                        update_user_expiry(username, new_expiry_date.strftime("%Y-%m-%d") if new_expiry_date else None)
                        update_user_simulations(username, selected_simulations)
                        st.success(f"Configurações para {user_data.get('name', username)} guardadas!")
                        st.rerun()

    with tab2:
        st.subheader("Cadastrar Novo Utilizador")
        with st.form("new_user_form", clear_on_submit=True):
            st.write("Preencha os dados do novo aluno:")
            name = st.text_input("Nome Completo")
            new_username = st.text_input("Nome de Utilizador (para login)")
            new_password = st.text_input("Senha Provisória", type="password")
            access_expires_on = st.date_input("Data de expiração do acesso", min_value=datetime.date.today())
            
            submitted = st.form_submit_button("Cadastrar Utilizador")
            if submitted:
                if not all([name, new_username, new_password, access_expires_on]):
                    st.warning("Por favor, preencha todos os campos.")
                elif username_exists(new_username):
                    st.error("Este nome de utilizador já existe. Por favor, escolha outro.")
                else:
                    hashed_pw = hash_password(new_password)
                    new_user_data = {
                        "name": name,
                        "password_hash": hashed_pw,
                        "role": "user",
                        "available_simulations": [],
                        "access_expires_on": access_expires_on.strftime("%Y-%m-%d")
                    }
                    add_user(new_username, new_user_data)
                    st.success(f"Utilizador '{name}' cadastrado com sucesso!")
                    st.rerun()

    with tab3:
        st.subheader("Gestão de Bancos de Questões")
        DATA_DIR = Path(__file__).parent.parent / "data"
        DATA_DIR.mkdir(exist_ok=True)
        uploaded_files = st.file_uploader("Faça upload de novos bancos (JSON)", type="json", accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(DATA_DIR / uploaded_file.name, "wb") as f: f.write(uploaded_file.getbuffer())
                st.success(f"Ficheiro '{uploaded_file.name}' carregado!")
            st.rerun()
        
        st.write("**Bancos de Questões Atuais:**")
        current_banks = get_all_question_banks()
        st.info(f"Encontrados {len(current_banks)} bancos: {', '.join(f'`{b}`' for b in current_banks)}" if current_banks else "Nenhum banco de questões encontrado.")

    with tab4:
        st.subheader("Enviar Mensagem Global")
        st.write("Esta mensagem aparecerá na página inicial de todos os utilizadores.")
        with st.form("message_form", clear_on_submit=True):
            message = st.text_area("Digite a sua mensagem:", height=150)
            submitted = st.form_submit_button("Publicar Mensagem")
            if submitted:
                if message:
                    save_global_message(message)
                    st.success("Mensagem publicada com sucesso!")
                else:
                    st.warning("O campo de mensagem não pode estar vazio.")

