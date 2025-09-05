import sys
sys.path.append("app/utils")
from json_validator import load_questions_from_json

# Teste com JSON válido
print("\n--- Testando JSON válido ---")
valid_data, valid_error = load_questions_from_json("app/data/questions_example.json")
if valid_data:
    print("JSON válido carregado com sucesso.")
else:
    print(f"Erro ao carregar JSON válido: {valid_error}")

# Teste com JSON inválido (poucas alternativas)
print("\n--- Testando JSON inválido (poucas alternativas) ---")
invalid_data_few_alt, invalid_error_few_alt = load_questions_from_json("app/data/invalid_questions_too_few_alternatives.json")
if invalid_data_few_alt:
    print("Erro: JSON inválido carregado como válido.")
else:
    print(f"Erro esperado ao carregar JSON inválido: {invalid_error_few_alt}")
