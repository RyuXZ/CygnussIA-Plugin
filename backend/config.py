import os

# Configuración del servidor y Ollama
HOST = "127.0.0.1"
PORT = 8000
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Modelos por defecto (como fallback)
DEFAULT_TEXT_MODEL = "llama3"
DEFAULT_VISION_MODEL = "llava"

# Parámetros de procesamiento de imagen
MAX_RESOLUTION_4K = (3840, 2160)
MAX_RESOLUTION_8K = (7680, 4320)
ALLOWED_FORMATS = ["PNG", "JPEG"]