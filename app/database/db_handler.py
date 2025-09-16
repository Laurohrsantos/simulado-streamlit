import json
from pathlib import Path
import datetime

# --- CONFIGURAÇÃO DOS CAMINHOS ---
DB_DIR = Path(__file__).parent
DATA_DIR = DB_DIR.parent / "data"
USERS_FILE = DB_DIR / "users.json"
RESULTS_FILE = DB_DIR / "results.json"
MESSAGES_FILE = DB_DIR / "messages.json"

# Garante que os ficheiros JSON existem
for file_path in [USERS_FILE, RESULTS_FILE, MESSAGES_FILE]:
    if not file_path.exists():
        with open(file_path, "w") as f:
            json.dump({}, f)

def _load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_data(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- FUNÇÕES DE UTILIZADOR ---
def get_user(username):
    return _load_data(USERS_FILE).get(username)

def get_all_users():
    return _load_data(USERS_FILE)

def username_exists(username):
    """Verifica se um nome de utilizador já existe."""
    return username in _load_data(USERS_FILE)

def add_user(username, user_data):
    """Adiciona um novo utilizador ao ficheiro de utilizadores."""
    users = _load_data(USERS_FILE)
    users[username] = user_data
    _save_data(users, USERS_FILE)

def update_user_simulations(username, simulations):
    users = _load_data(USERS_FILE)
    if username in users:
        users[username]['available_simulations'] = simulations
        _save_data(users, USERS_FILE)

def update_user_expiry(username, expiry_date):
    users = _load_data(USERS_FILE)
    if username in users:
        users[username]['access_expires_on'] = expiry_date
        _save_data(users, USERS_FILE)

# --- FUNÇÕES DE RESULTADOS ---
def save_simulation_result(username, result_data):
    results = _load_data(RESULTS_FILE)
    if username not in results:
        results[username] = []
    result_data['date'] = datetime.datetime.now().isoformat()
    results[username].append(result_data)
    _save_data(results, RESULTS_FILE)

def get_user_results(username):
    return _load_data(RESULTS_FILE).get(username, [])

def get_all_results():
    """Devolve todos os resultados de todos os utilizadores."""
    return _load_data(RESULTS_FILE)

# --- FUNÇÕES DO BANCO DE QUESTÕES ---
def get_all_question_banks():
    if not DATA_DIR.exists():
        return []
    return [f.name for f in DATA_DIR.glob("*.json")]

# --- FUNÇÕES DE MENSAGENS ---
def save_global_message(message):
    """Guarda a mensagem global para todos os utilizadores."""
    message_data = {
        "global_message": message,
        "updated_at": datetime.datetime.now().isoformat()
    }
    _save_data(message_data, MESSAGES_FILE)

def get_global_message():
    """Lê a mensagem global."""
    return _load_data(MESSAGES_FILE)

