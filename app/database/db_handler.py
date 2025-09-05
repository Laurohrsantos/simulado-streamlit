import json
from pathlib import Path
import datetime
import os

# Define o caminho para os ficheiros de dados
DB_DIR = Path(__file__).parent
DATA_DIR = Path(__file__).parent.parent / "data"
USERS_FILE = DB_DIR / "users.json"
RESULTS_FILE = DB_DIR / "results.json"

# Garante que os ficheiros JSON existem
for file_path in [USERS_FILE, RESULTS_FILE]:
    if not file_path.exists():
        with open(file_path, "w") as f:
            json.dump({}, f)

def _load_data(file_path):
    """Carrega dados de um ficheiro JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_data(data, file_path):
    """Guarda dados num ficheiro JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Funções de Utilizador ---

def get_user(username):
    """Procura um utilizador pelo nome."""
    users = _load_data(USERS_FILE)
    return users.get(username)

def get_all_users():
    """Devolve um dicionário com todos os utilizadores."""
    return _load_data(USERS_FILE)

def update_user_simulations(username, simulations):
    """Atualiza a lista de simulados disponíveis para um utilizador."""
    users = _load_data(USERS_FILE)
    if username in users:
        users[username]['available_simulations'] = simulations
        _save_data(users, USERS_FILE)
        return True
    return False

# --- Funções de Resultados ---

def save_simulation_result(username, result_data):
    """Guarda o resultado detalhado de um simulado para um utilizador."""
    results = _load_data(RESULTS_FILE)
    if username not in results:
        results[username] = []
    
    result_data['date'] = datetime.datetime.now().isoformat()
    results[username].append(result_data)
    
    _save_data(results, RESULTS_FILE)

def get_user_results(username):
    """Procura todos os resultados de um utilizador."""
    results = _load_data(RESULTS_FILE)
    return results.get(username, [])

# --- Funções do Banco de Questões ---

def get_all_question_banks():
    """Devolve uma lista com os nomes de todos os ficheiros de questões."""
    if not DATA_DIR.exists():
        return []
    return [f.name for f in DATA_DIR.glob("*.json")]

