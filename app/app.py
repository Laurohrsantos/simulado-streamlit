import streamlit as st
from utils.auth import login, is_authenticated, get_user_role, logout
from views import pagina_inicial, novo_simulado, historico, administracao

def main():
    """Função principal que gere a autenticação e a navegação da aplicação."""
    st.set_page_config(layout="wide", page_title="Plataforma de Estudos")

    if not is_authenticated():
        st.title("Bem-vindo à Plataforma de Estudos")
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                success, message = login(username, password)
                if success:
                    st.rerun()
                else:
                    st.error(message)
    else:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.title(f"Olá, {st.session_state['name']}!")

        with col2:
            # espaço expansível
            spacer = st.container()
            spacer.write(" " * 50)  # cria altura
            
            if st.button("Sair", use_container_width=True, type="primary"):
                logout()
                st.rerun()

        tab_titles = ["🏠 Página Inicial", "📝 Novo Simulado", "📊 Histórico"]
        if get_user_role() == 'admin':
            tab_titles.append("⚙️ Administração")
        
        tab1, tab2, tab3, *admin_tab = st.tabs(tab_titles)

        with tab1:
            pagina_inicial.render_page()
        with tab2:
            novo_simulado.render_page()
        with tab3:
            historico.render_page()
        if get_user_role() == 'admin' and admin_tab:
            with admin_tab[0]:
                administracao.render_page()

if __name__ == "__main__":
    main()

