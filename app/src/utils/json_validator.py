import json

def validate_questions_json(json_data):
    if not isinstance(json_data, dict):
        return False, "O JSON deve ser um objeto (dicionário) onde as chaves são as áreas de conhecimento."

    for area, questions in json_data.items():
        if not isinstance(questions, list):
            return False, f"A área de conhecimento '{area}' deve conter uma lista de questões."

        for i, question_obj in enumerate(questions):
            if not isinstance(question_obj, dict):
                return False, f"A questão {i+1} na área '{area}' não é um objeto válido."
            if "id" not in question_obj or not isinstance(question_obj["id"], str):
                return False, f"A questão {i+1} na área '{area}' não possui um 'id' válido."
            if "questao" not in question_obj or not isinstance(question_obj["questao"], str):
                return False, f"A questão {i+1} na área '{area}' não possui um 'questao' válido."
            if "alternativas" not in question_obj or not isinstance(question_obj["alternativas"], list):
                return False, f"A questão {i+1} na área '{area}' não possui uma lista de 'alternativas' válida."

            alternatives = question_obj["alternativas"]
            if not (4 <= len(alternatives) <= 5):
                return False, f"A questão {i+1} na área '{area}' deve ter entre 4 e 5 alternativas. Encontrado: {len(alternatives)}."

            correct_answers_count = 0
            for j, alt in enumerate(alternatives):
                if not isinstance(alt, dict):
                    return False, f"A alternativa {j+1} da questão {i+1} na área '{area}' não é um objeto válido."
                if "texto" not in alt or not isinstance(alt["texto"], str):
                    return False, f"A alternativa {j+1} da questão {i+1} na área '{area}' não possui um 'texto' válido."
                if "correta" not in alt or not isinstance(alt["correta"], bool):
                    return False, f"A alternativa {j+1} da questão {i+1} na área '{area}' não possui um status 'correta' válido (True/False)."
                if alt["correta"]:
                    correct_answers_count += 1

            if correct_answers_count != 1:
                return False, f"A questão {i+1} na área '{area}' deve ter exatamente uma alternativa correta. Encontrado: {correct_answers_count}."

    return True, "JSON validado com sucesso."

def load_questions_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        is_valid, message = validate_questions_json(data)
        if is_valid:
            return data, None
        else:
            return None, message
    except FileNotFoundError:
        return None, "Arquivo JSON não encontrado."
    except json.JSONDecodeError:
        return None, "Erro ao decodificar o JSON. Verifique a sintaxe do arquivo."
    except Exception as e:
        return None, f"Ocorreu um erro inesperado ao carregar o JSON: {e}"


