import streamlit as st
from utils.auth import require_auth
from database.db_handler import get_user_results
import pandas as pd
import datetime


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Histórico de Resultados")
require_auth()

st.title("O Seu Histórico de Resultados")

username = st.session_state['username']
results = get_user_results(username)

if not results:
    st.info("Ainda não completou nenhum simulado. Vá para a página 'Novo Simulado' para começar!")
else:
    st.write(f"Total de simulados realizados: **{len(results)}**")
    
    results.reverse() # Mostra os mais recentes primeiro

    # --- GRÁFICO DE EVOLUÇÃO ---
    df_data = {
        "Data": [datetime.datetime.fromisoformat(r['date']).strftime('%d/%m/%Y %H:%M') for r in results],
        "Pontuação (%)": [r['score_percent'] for r in results],
    }
    df = pd.DataFrame(df_data).set_index("Data")
    
    st.subheader("Evolução do Desempenho")
    st.line_chart(df)

    # --- DETALHES DE CADA SIMULADO ---
    st.subheader("Detalhes dos Simulados Anteriores")
    for result in results:
        date_obj = datetime.datetime.fromisoformat(result['date'])
        date_str = date_obj.strftime("%d/%m/%Y às %H:%M")
        
        with st.expander(f"Simulado de {date_str} - {result['score_percent']:.2f}% de acerto"):
            col1, col2 = st.columns(2)
            col1.metric("Desempenho", f"{result['correct_answers']} / {result['total_questions']}")
            
            time_taken = result.get('time_taken_seconds', 0)
            minutes, seconds = int(time_taken // 60), int(time_taken % 60)
            col2.metric("Tempo", f"{minutes}m {seconds}s")
            
            st.write("**Revisão das Questões:**")
            if 'detailed_results' in result:
                for i, res_detail in enumerate(result['detailed_results']):
                    st.markdown(f"--- \n **Questão {i+1} ({res_detail['area']}):** {res_detail['question_obj']['questao']}")
                    color = "green" if res_detail['is_correct'] else "red"
                    st.markdown(f"<span style='color:{color};'>A sua resposta: {res_detail['user_answer'] or 'Não respondida'}</span>", unsafe_allow_html=True)
                    if not res_detail['is_correct']:
                        st.markdown(f"**Resposta correta:** {res_detail['correct_answer']}")
            else:
                st.info("Revisão detalhada não disponível para este simulado antigo.")

