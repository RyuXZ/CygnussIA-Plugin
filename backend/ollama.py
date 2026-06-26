import requests
from config import OLLAMA_URL

def get_installed_models() -> list:
    """Obtiene la lista dinámica de modelos instalados en Ollama."""
    endpoint = f"{OLLAMA_URL}/api/tags"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        models_data = response.json().get("models", [])
        return [model["name"] for model in models_data]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error obteniendo modelos de Ollama: {e}")

def generate_text(prompt: str, model: str) -> str:
    endpoint = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la conexión con Ollama: {e}")

def analyze_vision(prompt: str, image_b64: str, model: str) -> str:
    endpoint = f"{OLLAMA_URL}/api/generate"
    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error procesando visión en Ollama: {e}")