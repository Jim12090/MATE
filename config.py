import os


def load_local_env():
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_local_env()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-smart-farm'
    OLLAMA_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen3-vl:2b"
    DEFAULT_MODEL_ID = "ollama:qwen3-vl:2b"
    DEFAULT_PROVIDER = "openai_compatible"
    DEFAULT_PROVIDER_CONFIG = {
        "provider": "openai_compatible",
        "base_url": "https://aigateway.edgecloudapp.com/v1/5e5f121300c3ba95b4d2d8fefae0c38d/nxinyun_chat",
        "api_key": os.environ.get("AI_GATEWAY_API_KEY", ""),
        "preferred_model": "qwen3-vl:8b",
        "manual_models": ["qwen3-vl:8b"],
    }
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    TARGETS_FILE = os.path.join(os.getcwd(), 'targets.json')
    MODEL_SETTINGS_FILE = os.path.join(os.getcwd(), 'runtime_settings.json')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MODEL_CATALOG = [
        {
            "id": "ollama:qwen3-vl:2b",
            "label": "Ollama / qwen3-vl:2b",
            "provider": "ollama",
            "model": "qwen3-vl:2b",
            "base_url": OLLAMA_BASE_URL,
            "is_default": True,
        },
        {
            "id": "openai:qwen3-vl:8b",
            "label": "AI Gateway / qwen3-vl:8b",
            "provider": "openai_compatible",
            "model": "qwen3-vl:8b",
            "base_url": "https://aigateway.edgecloudapp.com/v1/5e5f121300c3ba95b4d2d8fefae0c38d/nxinyun_chat",
            "api_key": os.environ.get("AI_GATEWAY_API_KEY", ""),
            "is_default": False,
        },
    ]
