# app.py

import streamlit as st
import json
import random
import time
import os  # type: ignore
from pathlib import Path 


def render_admin_page():
    """Renderiza a página de Administração."""
    st.header("Área Administrativa")
    st.subheader("Upload de Banco de Questões (JSON)")
    uploaded_file = st.file_uploader("Escolha um arquivo JSON", type=["json"])

    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8")
            questions_data = json.loads(file_content)
            load_and_set_questions(
                questions_data, 
                "Arquivo JSON validado e carregado com sucesso!", 
                st
            )
        except json.JSONDecodeError:
            st.error("Erro ao decodificar o JSON. Verifique a sintaxe do arquivo.")
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")
    
    st.subheader("Configurações do Simulado")
    max_questions = 100 
    if "questions_data" in st.session_state and st.session_state.questions_data:
        try:
            total_available = sum(len(v) for v in st.session_state.questions_data.values())
            max_questions = total_available if total_available > 0 else 1
        except Exception:
            max_questions = 100

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

def render_question_bank_page():
    """Renderiza a página do Banco de Questões."""
    st.header("Carregar Banco de Questões Local")
    
    try:
        current_dir = Path(__file__).parent
        DATA_DIR = current_dir.parent / 'data'
        
        if not DATA_DIR.is_dir():
            st.error(f"O diretório de dados esperado não foi encontrado em: '{DATA_DIR}'")
            st.info("Por favor, crie uma pasta chamada 'data' no mesmo nível da pasta 'src' do seu projeto.")
            return

        available_files = [f.name for f in DATA_DIR.glob('*.json')]
        
        if not available_files:
            st.warning(f"Nenhum banco de questões (.json) encontrado no diretório '{DATA_DIR}/'.")
            st.info("Para usar esta funcionalidade, adicione arquivos de questões em formato JSON na pasta 'data' do seu projeto.")
        else:
            selected_file = st.selectbox("Selecione um banco de questões:", available_files)
            
            if st.button("Carregar Banco Selecionado", type="primary"):
                file_path = DATA_DIR / selected_file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        questions_data = json.load(f)
                    load_and_set_questions(
                        questions_data,
                        f"Banco de questões '{selected_file}' carregado com sucesso!",
                        st
                    )
                except json.JSONDecodeError:
                    st.error(f"Erro ao decodificar o JSON no arquivo '{selected_file}'. Verifique a sintaxe.")
                except Exception as e:
                    st.error(f"Erro inesperado ao carregar o arquivo: {str(e)}")

    except Exception as e:
        st.error(f"Não foi possível acessar o diretório de dados: {str(e)}")

def render_simulation_page():
    """Renderiza a página da Simulação."""
    st.header("Simulação de Prova")

    if "questions_data" not in st.session_state or not st.session_state.questions_data:
        st.warning("Carregue um banco de questões na área de Administração ou no Banco de Questões.")
        return

    if not st.session_state.get("selected_areas"):
        st.warning("Selecione as áreas de conhecimento na área de Administração.")
        return

    if not st.session_state.quiz_started:
        all_questions_with_area = []
        for area in st.session_state.selected_areas:
            if area in st.session_state.questions_data:
                for question in st.session_state.questions_data[area]:
                    all_questions_with_area.append({"area": area, "question": question})
        
        if not all_questions_with_area:
            st.error("Nenhuma questão disponível para as áreas selecionadas.")
            return

        num_questions = min(st.session_state.num_questions, len(all_questions_with_area))
        st.session_state.selected_questions_for_quiz = random.sample(all_questions_with_area, num_questions)
        st.session_state.user_answers = [None] * num_questions
        st.session_state.current_question_index = 0
        st.session_state.quiz_started = True
        st.session_state.quiz_finished = False
        st.session_state.results_calculated = False
        st.session_state.start_time = time.time()
        st.session_state.shuffled_alternatives = {}
        st.success(f"Simulado iniciado com {num_questions} questões!")
        st.rerun()

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
            is_answered = st.session_state.user_answers[i] is not None
            is_current = i == current_index
            button_label = f"{i+1}"
            button_type = "primary" if is_current else ("secondary" if not is_answered else "primary")
            
            if col.button(button_label, key=f"nav_{i}", type=button_type, use_container_width=True):
                st.session_state.current_question_index = i
                st.rerun()
        
        st.sidebar.divider()
        
        if st.sidebar.button("Finalizar Simulado Agora", type="primary", use_container_width=True):
            st.session_state.confirm_finish = True
            st.rerun()

        if st.session_state.get("confirm_finish"):
            st.sidebar.warning("Você tem certeza que deseja finalizar?")
            col1, col2 = st.sidebar.columns(2)
            if col1.button("Sim, finalizar", key="confirm_yes", use_container_width=True):
                st.session_state.quiz_finished = True
                del st.session_state.confirm_finish
                st.rerun()
            if col2.button("Não, voltar", key="confirm_no", use_container_width=True):
                del st.session_state.confirm_finish
                st.rerun()
                
    if not st.session_state.quiz_finished and current_index < len(questions):
        question_info = questions[current_index]
        question = question_info['question']
        
        st.subheader(f"Questão {current_index + 1}/{len(questions)}")
        st.write(f"**Área:** {question_info['area']}")
        st.write(question["questao"])

        if current_index not in st.session_state.shuffled_alternatives:
            alts = question["alternativas"].copy()
            random.shuffle(alts)
            st.session_state.shuffled_alternatives[current_index] = alts
        
        alternatives = st.session_state.shuffled_alternatives[current_index]
        
        def update_answer():
            st.session_state.user_answers[current_index] = st.session_state[f"q_{current_index}"]

        st.radio(
            "Selecione sua resposta:",
            [alt["texto"] for alt in alternatives],
            index=[alt["texto"] for alt in alternatives].index(st.session_state.user_answers[current_index]) if st.session_state.user_answers[current_index] else None,
            key=f"q_{current_index}",
            on_change=update_answer
        )

        st.progress((current_index + 1) / len(questions))
        
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
                if st.button("Finalizar Simulado", type="primary", use_container_width=True):
                    st.session_state.quiz_finished = True
                    st.rerun()

    elif st.session_state.quiz_finished:
        if not st.session_state.results_calculated:
            correct = 0
            area_performance = {} 
            st.session_state.results = []
            
            for i, q_info in enumerate(questions):
                q = q_info['question']
                area = q_info['area']

                if area not in area_performance:
                    area_performance[area] = {'correct': 0, 'total': 0}
                area_performance[area]['total'] += 1
                
                correct_answer = next(a["texto"] for a in q["alternativas"] if a["correta"])
                is_correct = st.session_state.user_answers[i] == correct_answer
                
                if is_correct:
                    correct += 1
                    area_performance[area]['correct'] += 1
                    
                st.session_state.results.append({
                    "question_obj": q,
                    "area": area,
                    "user_answer": st.session_state.user_answers[i],
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                })
            
            st.session_state.correct_count = correct
            
            study_recommendations = []
            for area, stats in area_performance.items():
                if stats['total'] > 0 and stats['correct'] < stats['total']:
                    errors = stats['total'] - stats['correct']
                    error_percentage = (errors / stats['total']) * 100
                    study_recommendations.append(
                        f"**{area}**: Você errou {errors} de {stats['total']} questão(ões) ({error_percentage:.0f}% de erro)."
                    )
            st.session_state.study_recommendations = study_recommendations
            st.session_state.results_calculated = True
        
        st.header("Resultado Final")
        col1, col2 = st.columns(2)
        col1.metric("Acertos", f"{st.session_state.correct_count}/{len(questions)}")
        col2.metric("Percentual de Acerto", f"{(st.session_state.correct_count/len(questions))*100:.1f}%")
        
        elapsed_time = time.time() - st.session_state.start_time
        mins, secs = int(elapsed_time // 60), int(elapsed_time % 60)
        st.write(f"**Tempo total:** {mins:02d}m {secs:02d}s")

        st.subheader("Recomendações de Estudo")
        if not st.session_state.study_recommendations:
            st.success("Parabéns! Você acertou todas as questões. Continue com o ótimo trabalho! 🎉")
        else:
            st.warning("Foco nos estudos! Sugerimos revisar os seguintes tópicos com base no seu desempenho:")
            for recommendation in st.session_state.study_recommendations:
                st.markdown(f"- {recommendation}")

        st.subheader("Revisão das Questões")
        for i, result in enumerate(st.session_state.results):
            with st.expander(f"Questão {i+1} ({result['area']}) - {'Correta' if result['is_correct'] else 'Incorreta'}", expanded=False):
                st.write(f"**Enunciado:** {result['question_obj']['questao']}")
                st.markdown(f"**Sua resposta:** {result['user_answer'] or 'Não respondida'}")
                
                if not result['is_correct']:
                    st.markdown(f"**Resposta correta:** {result['correct_answer']}")
                
                
                # Procura pela justificativa no JSON e só a exibe se existir.
                correct_alt_obj = next((alt for alt in result['question_obj']['alternativas'] if alt['correta']), None)
                if correct_alt_obj and 'justificativa' in correct_alt_obj and correct_alt_obj['justificativa']:
                    st.info(f"**Justificativa:** {correct_alt_obj['justificativa']}")

        col1_final, col2_final = st.columns(2)
        if col1_final.button("Fazer Novo Simulado", type="primary", use_container_width=True):
            keys_to_reset = ['quiz_started', 'quiz_finished', 'results_calculated', 'current_question_index', 'user_answers', 'selected_questions_for_quiz', 'shuffled_alternatives', 'results', 'correct_count', 'study_recommendations', 'confirm_finish']
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            
        
        report_content = f"Resultado do Simulado\n\n"
        report_content += f"Acertos: {st.session_state.correct_count}/{len(questions)}\n"
        report_content += f"Percentual de Acerto: {(st.session_state.correct_count/len(questions))*100:.1f}%\n"
        report_content += f"Tempo Total: {mins:02d}m {secs:02d}s\n\n"
        report_content += "Recomendações de Estudo:\n"
        if st.session_state.study_recommendations:
            for recommendation in st.session_state.study_recommendations:
                report_content += f"- {recommendation.replace('**', '')}\n"
        else:
            report_content += "- Nenhuma, você acertou tudo!\n"

        col2_final.download_button(
            label="Baixar Relatório (.txt)",
            data=report_content,
            file_name="relatorio_simulado.txt",
            mime="text/plain",
            use_container_width=True
        )


def load_and_set_questions(questions_data, success_message, st_obj):
    """
    Valida os dados das questões e, se forem válidos,
    atualiza o estado da sessão para iniciar um novo simulado.
    """
    from utils.json_validator import validate_questions_json # Movido para dentro para evitar import circular se houver
    is_valid, message = validate_questions_json(questions_data)
    if is_valid:
        st_obj.success(success_message)
        st_obj.session_state.questions_data = questions_data
        # Resetar estado do quiz e outras configurações
        st_obj.session_state.quiz_started = False
        st_obj.session_state.quiz_finished = False
        st_obj.session_state.results_calculated = False
        st_obj.session_state.current_question_index = 0
        st_obj.session_state.user_answers = []
        st_obj.session_state.selected_questions_for_quiz = []
        st_obj.session_state.shuffled_alternatives = {}
        if "questions_data" in st_obj.session_state:
            st_obj.session_state.selected_areas = list(st_obj.session_state.questions_data.keys())
    else:
        st_obj.error(f"Erro de validação: {message}")


def main():
    """Função principal que inicializa e direciona o app."""
    st.set_page_config(layout="wide", page_title="Simulador de Provas")
    st.title("Simulador de Provas Online")

    # Inicialização de variáveis de sessão
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'results_calculated' not in st.session_state:
        st.session_state.results_calculated = False

    st.sidebar.title("Navegação Principal")
    page = st.sidebar.radio("Ir para", ["Administração", "Banco de Questões", "Simulação"])

    if page == "Administração":
        render_admin_page()
    elif page == "Banco de Questões":
        render_question_bank_page()
    elif page == "Simulação":
        render_simulation_page()

if __name__ == "__main__":
    main()