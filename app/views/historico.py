import streamlit as st
from database.db_handler import get_user_results
import pandas as pd
import datetime

def render_page():
    """Renderiza a página de histórico de resultados do utilizador."""
    st.title("📊 O Seu Histórico de Resultados")

    username = st.session_state['username']
    results = get_user_results(username)

    if not results:
        st.info("Ainda não completou nenhum simulado. Vá para a aba 'Novo Simulado' para começar!")
        return

    # --- GRÁFICO DE DESEMPENHO GERAL POR ÁREA ---
    area_performance = {}
    for result in results:
        for area, stats in result.get('area_performance', {}).items():
            if area not in area_performance: area_performance[area] = {'correct': 0, 'total': 0}
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

    st.divider()
    
    # --- GRÁFICO DE EVOLUÇÃO ---
    st.subheader("Evolução do Desempenho ao Longo do Tempo")
    df_data = {
        "Data": [datetime.datetime.fromisoformat(r['date']) for r in results],
        "Pontuação (%)": [r['score_percent'] for r in results],
    }
    df_evolution = pd.DataFrame(df_data).set_index("Data")
    st.line_chart(df_evolution)
    
    st.divider()

    # --- DETALHES DE CADA SIMULADO ---
    st.subheader("Análise Detalhada dos Simulados")
    results.reverse() # Mostra os mais recentes primeiro
    for result in results:
        # ... (código existente para expander, sem alterações)
        date_obj = datetime.datetime.fromisoformat(result['date'])
        date_str = date_obj.strftime("%d/%m/%Y às %H:%M")
        with st.expander(f"Simulado de {date_str} - {result['score_percent']:.2f}% de acerto"):
            # ... (resto do código de detalhes)
            pass # Adicione o seu código de detalhe de resultado aqui

