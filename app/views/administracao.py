import streamlit as st
from pathlib import Path
from database.db_handler import get_all_question_banks, get_all_users, update_user_simulations, update_user_expiry
import datetime

def render_page():
    """Renderiza o painel de administração."""
    st.title("Painel de Administração")

    # --- GESTÃO DE BANCOS DE QUESTÕES ---
    with st.container(border=True):
        # ... (código existente de upload, sem alterações)
        st.subheader("Gestão de Bancos de Questões")
        DATA_DIR = Path(__file__).parent.parent / "data"
        DATA_DIR.mkdir(exist_ok=True)
        # ... (resto do código de upload)

    # --- GESTÃO DE UTILIZADORES ---
    with st.container(border=True):
        st.subheader("Gerir Acesso dos Utilizadores")
        
        all_users = get_all_users()
        all_banks = get_all_question_banks()
        users_to_manage = {name: data for name, data in all_users.items() if data['role'] != 'admin'}

        if not users_to_manage:
            st.info("Nenhum utilizador padrão encontrado para gerir.")
            return

        for username, user_data in users_to_manage.items():
            with st.expander(f"Gerir Utilizador: **{user_data.get('name', username)}**"):
                # --- Controlo de Acesso por Data ---
                st.markdown("**Validade do Acesso**")
                current_expiry_str = user_data.get('access_expires_on')
                current_expiry_date = None
                if current_expiry_str:
                    current_expiry_date = datetime.datetime.strptime(current_expiry_str, "%Y-%m-%d").date()

                new_expiry_date = st.date_input(
                    "Definir data de expiração do acesso:",
                    value=current_expiry_date,
                    min_value=datetime.date.today(),
                    key=f"date_{username}"
                )
                
                # --- Controlo de Acesso a Simulados ---
                st.markdown("**Simulados Disponíveis**")
                if not all_banks:
                    st.warning("Nenhum banco de questões disponível para ser atribuído.")
                else:
                    current_simulations = user_data.get('available_simulations', [])
                    selected_simulations = st.multiselect(
                        f"Selecione os simulados:",
                        options=all_banks,
                        key=f"sims_{username}"
                    )
                
                if st.button("Guardar Alterações", key=f"save_{username}"):
                    # Atualiza a data de expiração
                    update_user_expiry(username, new_expiry_date.strftime("%Y-%m-%d") if new_expiry_date else None)
                    # Atualiza os simulados
                    if all_banks:
                        update_user_simulations(username, selected_simulations)
                    st.success(f"Configurações para {user_data.get('name', username)} guardadas!")
                    st.rerun()

