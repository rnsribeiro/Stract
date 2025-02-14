import requests
import os


BASE_URL = os.getenv("URL") # Obtem a url base da api de consulta
BEARER_TOKEN = os.getenv("API_TOKEN")  # Substitua pelo seu token real

def get_platforms():
    """Obtém a lista de plataformas disponíveis com autenticação."""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{BASE_URL}platforms", headers=headers)
        response.raise_for_status()
        return response.json().get("platforms", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar plataformas: {e}")
        return []  # Retorna uma lista vazia em caso de erro