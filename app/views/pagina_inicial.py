import streamlit as st
from database.db_handler import get_user_results, get_global_message, get_all_users, get_all_results
import pandas as pd
from datetime import datetime

def render_admin_dashboard():
    """Renderiza o dashboard específico para administradores."""
    st.subheader("Dashboard Administrativo")
    
    all_users = get_all_users()
    all_results = get_all_results()
    
    # Métrica 1: Número de Alunos
    student_count = len([u for u, d in all_users.items() if d['role'] == 'user'])
    
    # Métrica 2: Tempo Médio de Estudo
    total_time_seconds = 0
    total_simulations = 0
    for user, results in all_results.items():
        total_simulations += len(results)
        total_time_seconds += sum(r.get('time_taken_seconds', 0) for r in results)
        
    avg_time_seconds = total_time_seconds / total_simulations if total_simulations > 0 else 0
    avg_time_min, avg_time_sec = int(avg_time_seconds // 60), int(avg_time_seconds % 60)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="👨‍🎓 Alunos Ativos", value=student_count)
    with col2:
        st.metric(label="⏱️ Tempo Médio de Simulado (Geral)", value=f"{avg_time_min}m {avg_time_sec}s")

def render_user_dashboard():
    """Renderiza o dashboard padrão para utilizadores."""
    # Exibe a mensagem global, se houver
    message_data = get_global_message()
    if message_data and message_data.get("global_message"):
        st.info(f"**Aviso do Administrador:** {message_data['global_message']}")

    if (data_access := st.session_state.get("access_expires_on")):
         data_formatada = datetime.strptime(data_access, '%Y-%m-%d').strftime('%d/%m/%Y')
         st.success(f"O seu acesso está liberado até: **{data_formatada}**")

    st.subheader("O seu painel de estudos")
    
    results = get_user_results(st.session_state['username'])
    if not results:
        st.info("Ainda não completou nenhum simulado. Comece um novo na aba 'Novo Simulado' para ver o seu progresso aqui!")
        return

    # --- MÉTRICAS GERAIS ---
    total_simulados = len(results)
    avg_score = sum(r['score_percent'] for r in results) / total_simulados
    total_time_seconds = sum(r.get('time_taken_seconds', 0) for r in results)
    avg_time_seconds = total_time_seconds / total_simulados if total_simulados > 0 else 0
    avg_time_min, avg_time_sec = int(avg_time_seconds // 60), int(avg_time_seconds % 60)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📝 Total de Simulados", value=total_simulados)
    with col2:
        st.metric(label="🎯 Média Geral", value=f"{avg_score:.2f}%")
    with col3:
        st.metric(label="⏱️ Tempo Médio", value=f"{avg_time_min}m {avg_time_sec}s")
    st.divider()

    # --- GRÁFICO DE DESEMPENHO POR ÁREA ---
    area_performance = {}
    for result in results:
        for area, stats in result.get('area_performance', {}).items():
            if area not in area_performance:
                area_performance[area] = {'correct': 0, 'total': 0}
            area_performance[area]['correct'] += stats['correct']
            area_performance[area]['total'] += stats['total']

    if area_performance:
        st.subheader("Desempenho Geral por Área")
        area_data = {"Área": [], "Acertos (%)": []}
        for area, stats in area_performance.items():
            percentage = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            area_data["Área"].append(area)
            area_data["Acertos (%)"].append(percentage)
        df_area = pd.DataFrame(area_data).set_index("Área")
        st.bar_chart(df_area)

def render_page():
    """Renderiza a página inicial, mostrando o dashboard apropriado para o papel do utilizador."""
    if st.session_state['role'] == 'admin':
        render_admin_dashboard()
    else:
        render_user_dashboard()

