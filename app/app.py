import streamlit as st
from utils.auth import login, is_authenticated, get_user_role, logout

def main():
    """Função principal que gere a autenticação e a navegação da aplicação."""
    st.set_page_config(layout="wide", page_title="Plataforma de Estudos")

    def page():
        st.write("Hello")

    if not is_authenticated():
        
        st.navigation([page], position = "hidden", expanded = False)
        
        st.title("Bem-vindo à Plataforma de Estudos")
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Utilizador")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                if login(username, password):
                    st.rerun()
                else:
                    st.error("Utilizador ou senha incorretos.")
    else:
        # st.set_page_config(initial_sidebar_state ="expanded")
        pages = [
            st.Page("views/0_Pagina_Inicial.py", title="Página Inicial", icon="🏠"),
            st.Page("views/1_Novo_Simulado.py", title="Novo Simulado", icon="📝"),
            st.Page("views/2_Historico_de_Resultados.py", title="Histórico", icon="📊"),
        ]
        
        if get_user_role() == 'admin':
            pages.append(st.Page("views/3_Administracao.py", title="Administração", icon="⚙️"))
        
        # Executa a página que o utilizador selecionou no menu
        pg = st.navigation(pages)
        
        # --- Barra Lateral Centralizada ---
        # Desenha a sidebar com as informações do utilizador e o botão de logout
        st.sidebar.divider()
        st.sidebar.success(f"Sessão iniciada como: **{st.session_state['name']}**")
        st.sidebar.info(f"Nível de Acesso: **{st.session_state['role']}**")
        
        # Lógica de logout 
        if st.sidebar.button("Logout", use_container_width=True):
            logout()
            st.rerun()

        
        pg.run()
    
   

if __name__ == "__main__":
    main()