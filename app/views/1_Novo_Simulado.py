import streamlit as st
import json
from pathlib import Path
import random
import time
from utils.auth import require_auth
from database.db_handler import get_user, get_all_question_banks, save_simulation_result


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Novo Simulado")
require_auth()

# Inicializa o estado do quiz
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

# --- FUNÇÕES AUXILIARES ---
def load_questions_from_banks(selected_banks):
    """Carrega questões dos bancos de dados selecionados."""
    all_questions = []
    data_dir = Path(__file__).parent.parent / "data"
    for bank_name in selected_banks:
        file_path = data_dir / bank_name
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for area, questions in data.items():
                    for q in questions:
                        all_questions.append({"area": area, "question": q, "source_bank": bank_name})
    return all_questions

def reset_quiz():
    """Reinicia o estado da sessão para permitir um novo simulado."""
    keys_to_reset = ['quiz_started', 'quiz_finished', 'selected_questions', 'user_answers', 'current_question_index', 'shuffled_alts', 'full_result']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- RENDERIZAÇÃO DA PÁGINA ---

# ETAPA 1: ECRÃ DE CONFIGURAÇÃO DO SIMULADO
if not st.session_state.quiz_started:
    st.header("Criar Novo Simulado Personalizado")
    
    user_info = get_user(st.session_state['username'])
    
    if st.session_state['role'] == 'admin':
        available_banks = get_all_question_banks()
        st.info("Como administrador, tem acesso a todos os bancos de questões.")
    else:
        available_banks = user_info.get('available_simulations', [])

    if not available_banks:
        st.warning("Não tem acesso a nenhum banco de questões no momento.")
        st.info("Por favor, peça a um administrador para libertar o seu acesso.")
    else:
        with st.form("simulado_config"):
            selected_banks = st.multiselect(
                "Selecione os bancos de questões para este simulado:",
                available_banks,
                default=available_banks if len(available_banks) == 1 else []
            )
            num_questions = st.slider("Número de questões desejado:", 5, 100, 20)
            submitted = st.form_submit_button("Iniciar Simulado")

            if submitted:
                if not selected_banks:
                    st.error("Selecione pelo menos um banco de questões.")
                else:
                    all_q = load_questions_from_banks(selected_banks)
                    if not all_q:
                        st.error("Nenhuma questão encontrada nos bancos selecionados.")
                    else:
                        num_to_sample = min(num_questions, len(all_q))
                        st.session_state.selected_questions = random.sample(all_q, num_to_sample)
                        st.session_state.user_answers = [None] * num_to_sample
                        st.session_state.current_question_index = 0
                        st.session_state.quiz_started = True
                        st.session_state.quiz_finished = False
                        st.session_state.start_time = time.time()
                        st.session_state.shuffled_alts = {}
                        st.rerun()

# ETAPA 2: DURANTE O SIMULADO
elif not st.session_state.get('quiz_finished', False):
    questions = st.session_state.selected_questions
    current_idx = st.session_state.current_question_index
    question_info = questions[current_idx]
    question = question_info['question']

    # --- RENDERIZAÇÃO DA BARRA LATERAL DE NAVEGAÇÃO ---
    st.sidebar.subheader("Navegar Questões")
    cols = st.sidebar.columns(5)
    for i in range(len(questions)):
        col = cols[i % 5]
        is_answered = st.session_state.user_answers[i] is not None
        btn_type = "primary" if i == current_idx else ("secondary" if not is_answered else "primary")
        if col.button(f"{i+1}", key=f"nav_{i}", type=btn_type, use_container_width=True):
            st.session_state.current_question_index = i
            st.rerun()

    # --- RENDERIZAÇÃO DA QUESTÃO ATUAL ---
    st.header(f"Questão {current_idx + 1}/{len(questions)}")
    st.write(f"**Área:** {question_info['area']}")
    st.markdown(f"> {question['questao']}")

    if current_idx not in st.session_state.shuffled_alts:
        alts = question["alternativas"].copy()
        random.shuffle(alts)
        st.session_state.shuffled_alts[current_idx] = alts
    
    alternatives = st.session_state.shuffled_alts[current_idx]
    
    def update_answer():
        st.session_state.user_answers[current_idx] = st.session_state[f"q_{current_idx}"]

    st.radio(
        "Selecione a sua resposta:", [a["texto"] for a in alternatives],
        key=f"q_{current_idx}", on_change=update_answer,
        index=[a["texto"] for a in alternatives].index(st.session_state.user_answers[current_idx]) if st.session_state.user_answers[current_idx] else None
    )
    
    # --- NAVEGAÇÃO E FINALIZAÇÃO ---
    col1, _, col3 = st.columns([1, 2, 1])
    if col1.button("<< Anterior", disabled=(current_idx == 0), use_container_width=True):
        st.session_state.current_question_index -= 1
        st.rerun()
    if col3.button("Próxima >>", disabled=(current_idx == len(questions) - 1), use_container_width=True):
        st.session_state.current_question_index += 1
        st.rerun()

    st.divider()
    if st.button("Finalizar e Ver Resultado", type="primary", use_container_width=True):
        st.session_state.quiz_finished = True
        st.rerun()

# ETAPA 3: ECRÃ DE RESULTADOS E REVISÃO
else:
    if 'full_result' not in st.session_state:
        # Cálculo do resultado
        correct = 0
        detailed_results = []
        area_performance = {}

        for i, q_info in enumerate(st.session_state.selected_questions):
            q = q_info['question']
            area = q_info['area']
            
            if area not in area_performance: area_performance[area] = {'correct': 0, 'total': 0}
            area_performance[area]['total'] += 1
            
            correct_answer = next((a["texto"] for a in q["alternativas"] if a["correta"]), None)
            user_answer = st.session_state.user_answers[i]
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct += 1
                area_performance[area]['correct'] += 1
            
            detailed_results.append({
                "question_obj": q, "area": area, "user_answer": user_answer,
                "correct_answer": correct_answer, "is_correct": is_correct
            })

        total = len(st.session_state.selected_questions)
        score = (correct / total) * 100 if total > 0 else 0
        
        # Guarda o resultado completo para a sessão e para o DB
        st.session_state.full_result = {
            "total_questions": total, "correct_answers": correct, "score_percent": score,
            "time_taken_seconds": time.time() - st.session_state.start_time,
            "area_performance": area_performance, "detailed_results": detailed_results
        }
        save_simulation_result(st.session_state['username'], st.session_state.full_result)

    # --- Renderização da página de resultados ---
    result = st.session_state.full_result
    st.header("Resultado Final do Simulado")
    
    col1, col2 = st.columns(2)
    col1.metric("Acertos", f"{result['correct_answers']} / {result['total_questions']}")
    col2.metric("Pontuação", f"{result['score_percent']:.2f}%")

    st.subheader("Recomendações de Estudo")
    recommendations = [f"**{area}**: Errou {stats['total'] - stats['correct']} de {stats['total']}." 
                       for area, stats in result['area_performance'].items() if stats['correct'] < stats['total']]
    if not recommendations:
        st.success("Parabéns! Desempenho excelente! 🎉")
    else:
        st.warning("Sugerimos focar os seus estudos nas seguintes áreas:")
        for rec in recommendations: st.markdown(f"- {rec}")

    st.subheader("Revisão Detalhada")
    for i, res in enumerate(result['detailed_results']):
        with st.expander(f"Questão {i+1} ({res['area']}) - {'Correta' if res['is_correct'] else 'Incorreta'}"):
            st.markdown(f"**Enunciado:** {res['question_obj']['questao']}")
            st.markdown(f"**A sua resposta:** {res['user_answer'] or 'Não respondida'}")
            if not res['is_correct']:
                st.markdown(f"**Resposta correta:** {res['correct_answer']}")
            
            correct_alt = next((a for a in res['question_obj']['alternativas'] if a['correta']), None)
            if correct_alt and 'justificativa' in correct_alt and correct_alt['justificativa']:
                st.info(f"**Justificativa:** {correct_alt['justificativa']}")
    
    st.divider()
    if st.button("Fazer Novo Simulado", use_container_width=True, type="primary"):
        reset_quiz()

