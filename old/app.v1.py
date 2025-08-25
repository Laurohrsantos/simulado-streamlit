import streamlit as st
from utils.json_validator import validate_questions_json
import json
import random
import time

def main():
    st.set_page_config(layout="wide")
    st.title("Simulador de Provas Online")

    # Inicialização de variáveis de sessão
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'results_calculated' not in st.session_state:
        st.session_state.results_calculated = False

    st.sidebar.title("Navegação Principal")
    page = st.sidebar.radio("Ir para", ["Administração", "Simulação"])

    if page == "Administração":
        st.header("Área Administrativa")
        st.subheader("Upload de Banco de Questões (JSON)")
        uploaded_file = st.file_uploader("Escolha um arquivo JSON", type=["json"])

        if uploaded_file is not None:
            try:
                file_content = uploaded_file.read().decode("utf-8")
                questions_data = json.loads(file_content)
                is_valid, message = validate_questions_json(questions_data)
                
                if is_valid:
                    st.success("Arquivo JSON validado e carregado com sucesso!")
                    st.session_state.questions_data = questions_data
                    # Resetar estado do quiz e outras configurações
                    st.session_state.quiz_started = False
                    st.session_state.quiz_finished = False
                    st.session_state.results_calculated = False
                    st.session_state.current_question_index = 0
                    st.session_state.user_answers = []
                    st.session_state.selected_questions_for_quiz = []
                    st.session_state.shuffled_alternatives = {}
                    if "questions_data" in st.session_state:
                        st.session_state.selected_areas = list(st.session_state.questions_data.keys())

                else:
                    st.error(f"Erro de validação: {message}")
            except json.JSONDecodeError:
                st.error("Erro ao decodificar o JSON. Verifique a sintaxe do arquivo.")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")
        elif "questions_data" not in st.session_state:
            st.info("Faça o upload de um arquivo JSON válido para começar.")
        
        st.subheader("Configurações do Simulado")

        # --- NOVO: SLIDER DINÂMICO PARA NÚMERO DE QUESTÕES ---
        max_questions = 100 # Valor padrão
        if "questions_data" in st.session_state:
            try:
                # Calcula o total de questões disponíveis no arquivo carregado
                total_available = sum(len(v) for v in st.session_state.questions_data.values())
                max_questions = total_available if total_available > 0 else 1
            except Exception:
                max_questions = 100

        # Garante que o valor atual não seja maior que o máximo
        current_value = st.session_state.get("num_questions", 10)
        if current_value > max_questions:
            current_value = max_questions

        st.session_state.num_questions = st.slider(
            "Número de Questões:", 
            min_value=1, 
            max_value=max_questions,
            value=current_value, 
            step=1
        )
        # --- FIM DO SLIDER ---

        st.session_state.num_alternatives_display = st.radio(
            "Alternativas por Questão:",
            options=[4, 5],
            index=[4, 5].index(st.session_state.get("num_alternatives_display", 4))
        )

        if "questions_data" in st.session_state and st.session_state.questions_data:
            available_areas = list(st.session_state.questions_data.keys())
            if available_areas:
                st.subheader("Áreas de Conhecimento")
                st.write("Selecione as áreas para o simulado:")
                
                if "selected_areas" not in st.session_state:
                    st.session_state.selected_areas = available_areas.copy()
                
                selection_before_render = st.session_state.selected_areas[:]

                if len(available_areas) > 1:
                    all_areas_selected = len(st.session_state.selected_areas) == len(available_areas)
                    select_all = st.checkbox("Selecionar Todas as Áreas", value=all_areas_selected)

                    if select_all:
                        st.session_state.selected_areas = available_areas.copy()
                    elif all_areas_selected and not select_all:
                         st.session_state.selected_areas = []

                col1, col2 = st.columns(2)
                mid_point = len(available_areas) // 2 + (len(available_areas) % 2)
                
                def render_checkbox(area, column):
                    is_selected = column.checkbox(
                        area,
                        value=area in st.session_state.selected_areas,
                        key=f"area_{area}"
                    )
                    if is_selected and area not in st.session_state.selected_areas:
                        st.session_state.selected_areas.append(area)
                    elif not is_selected and area in st.session_state.selected_areas:
                        st.session_state.selected_areas.remove(area)

                for area in available_areas[:mid_point]:
                    render_checkbox(area, col1)
                
                for area in available_areas[mid_point:]:
                    render_checkbox(area, col2)
                
                if selection_before_render != st.session_state.selected_areas:
                    st.rerun()

            else:
                st.warning("Nenhuma área encontrada no JSON.")
                st.session_state.selected_areas = []
        else:
            st.info("Carregue um arquivo JSON para selecionar áreas.")
            st.session_state.selected_areas = []

    elif page == "Simulação":
        st.header("Simulação de Prova")

        if "questions_data" not in st.session_state or not st.session_state.questions_data:
            st.warning("Carregue um banco de questões na área administrativa.")
            return

        if not st.session_state.get("selected_areas"):
            st.warning("Selecione as áreas de conhecimento na área administrativa.")
            return

        if not st.session_state.quiz_started:
            all_questions = []
            for area in st.session_state.selected_areas:
                if area in st.session_state.questions_data:
                    all_questions.extend(st.session_state.questions_data[area])
            
            if not all_questions:
                st.error("Nenhuma questão disponível para as áreas selecionadas.")
                return

            num_questions = min(st.session_state.num_questions, len(all_questions))
            st.session_state.selected_questions_for_quiz = random.sample(all_questions, num_questions)
            st.session_state.user_answers = [None] * num_questions
            st.session_state.current_question_index = 0
            st.session_state.quiz_started = True
            st.session_state.quiz_finished = False
            st.session_state.results_calculated = False
            st.session_state.start_time = time.time()
            st.session_state.shuffled_alternatives = {}

            st.success(f"Simulado iniciado com {num_questions} questões!")

        questions = st.session_state.selected_questions_for_quiz
        current_index = st.session_state.current_question_index

        if st.session_state.quiz_started and not st.session_state.quiz_finished:
            elapsed_time = time.time() - st.session_state.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            st.sidebar.write(f"**Tempo Decorrido:** {minutes:02d}:{seconds:02d}")
            st.sidebar.divider()

            st.sidebar.subheader("Navegar Questões")
            cols = st.sidebar.columns(5) 
            for i in range(len(questions)):
                col = cols[i % 5]
                button_label = f"✅ {i+1}" if st.session_state.user_answers[i] is not None else str(i + 1)
                button_type = "primary" if i == current_index else "secondary"
                
                if col.button(button_label, key=f"nav_{i}", type=button_type, use_container_width=True):
                    st.session_state.current_question_index = i
                    st.rerun()
            
            st.sidebar.divider()
            # --- NOVO: BOTÃO PARA FINALIZAR NA BARRA LATERAL ---
            if st.sidebar.button("Finalizar Simulado Agora", type="primary", use_container_width=True):
                st.session_state.quiz_finished = True
                st.rerun()
            # --- FIM DO BOTÃO ---

        if not st.session_state.quiz_finished and current_index < len(questions):
            question = questions[current_index]
            
            st.subheader(f"Questão {current_index + 1}/{len(questions)}")
            st.write(question["questao"])

            if current_index not in st.session_state.shuffled_alternatives:
                alts = question["alternativas"].copy()
                random.shuffle(alts)
                st.session_state.shuffled_alternatives[current_index] = alts
            
            alternatives = st.session_state.shuffled_alternatives[current_index]
            
            # --- ALTERADO: REMOVIDO AVANÇO AUTOMÁTICO ---
            def update_answer():
                st.session_state.user_answers[current_index] = st.session_state[f"q_{current_index}"]

            st.radio(
                "Selecione sua resposta:",
                [alt["texto"] for alt in alternatives],
                index=[alt["texto"] for alt in alternatives].index(st.session_state.user_answers[current_index]) if st.session_state.user_answers[current_index] else None,
                key=f"q_{current_index}",
                on_change=update_answer
            )
            # --- FIM DA ALTERAÇÃO ---

            st.progress((current_index + 1) / len(questions))
            st.write(f"Progresso: {current_index + 1}/{len(questions)}")
            
            # --- NOVO: LÓGICA DE NAVEGAÇÃO MANUAL E BOTÃO FINALIZAR ---
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Anterior", disabled=(current_index == 0), use_container_width=True):
                    st.session_state.current_question_index -= 1
                    st.rerun()
            
            with col3:
                if current_index < len(questions) - 1:
                    if st.button("Próxima", use_container_width=True):
                        st.session_state.current_question_index += 1
                        st.rerun()
                else:
                    # Botão Finalizar aparece apenas na última questão
                    if st.button("Finalizar Simulado", type="primary", use_container_width=True):
                        st.session_state.quiz_finished = True
                        st.rerun()
            # --- FIM DA NOVA LÓGICA ---


        elif st.session_state.quiz_finished:
            if not st.session_state.results_calculated:
                correct = 0
                st.session_state.results = []
                
                for i, q in enumerate(questions):
                    correct_answer = next(a["texto"] for a in q["alternativas"] if a["correta"])
                    is_correct = st.session_state.user_answers[i] == correct_answer
                    if is_correct:
                        correct += 1
                        
                    st.session_state.results.append({
                        "question": q["questao"],
                        "user_answer": st.session_state.user_answers[i],
                        "correct_answer": correct_answer,
                        "is_correct": is_correct,
                        "alternatives": q["alternativas"]
                    })
                
                st.session_state.correct_count = correct
                st.session_state.results_calculated = True
            
            st.header("Resultado Final")
            
            st.metric("Acertos", f"{st.session_state.correct_count}/{len(questions)}")
            st.metric("Percentual de Acerto", f"{(st.session_state.correct_count/len(questions))*100:.1f}%")
            
            elapsed_time = time.time() - st.session_state.start_time
            mins, secs = int(elapsed_time // 60), int(elapsed_time % 60)
            st.write(f"**Tempo total:** {mins:02d}m {secs:02d}s")

            st.subheader("Revisão das Questões")
            for i, result in enumerate(st.session_state.results):
                with st.expander(f"Questão {i+1} - {'Correta' if result['is_correct'] else 'Incorreta'}", expanded=False):
                    st.write(f"**Enunciado:** {result['question']}")
                    st.markdown(f"**Sua resposta:** {result['user_answer'] or 'Não respondida'}")
                    
                    if not result['is_correct']:
                        st.markdown(f"**Resposta correta:** {result['correct_answer']}")
                    
                    st.write("**Alternativas:**")
                    for alt in result['alternatives']:
                        if alt['correta']:
                            st.success(f"-> {alt['texto']} (Correta)")
                        else:
                            st.info(f"- {alt['texto']}")

            if st.button("Fazer Novo Simulado", type="primary"):
                st.session_state.quiz_started = False
                st.session_state.quiz_finished = False
                st.session_state.results_calculated = False
                st.session_state.current_question_index = 0
                st.rerun()

if __name__ == "__main__":
    main()
