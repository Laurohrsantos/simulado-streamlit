import streamlit as st
from database.db_handler import get_user_results
import pandas as pd
from datetime import datetime

def render_page():
    """Renderiza o dashboard da página inicial."""
    st.title("Bem-vindo ao seu painel de estudos. Aqui está um resumo do seu progresso.")

    if (data_access := st.session_state.get("access_expires_on")):
        st.badge(f"O seu acesso está liberado até: **{datetime.strptime(data_access, '%Y-%m-%d').strftime('%d/%m/%Y')}**")

    username = st.session_state['username']
    results = get_user_results(username)

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
        
        area_data = {
            "Área": [],
            "Acertos (%)": []
        }
        for area, stats in area_performance.items():
            percentage = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            area_data["Área"].append(area)
            area_data["Acertos (%)"].append(percentage)
        
        df_area = pd.DataFrame(area_data).set_index("Área")
        st.bar_chart(df_area)

