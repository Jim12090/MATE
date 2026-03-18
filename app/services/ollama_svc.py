import requests
from flask import current_app

class OllamaService:
    @staticmethod
    def list_models():
        base_url = current_app.config.get('OLLAMA_BASE_URL')
        try:
            resp = requests.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data.get('models', [])]
            return []
        except Exception as e:
            print(f"Ollama Connection Error: {e}")
            return []

    @staticmethod
    def generate(prompt, model=None, image_b64=None):
        base_url = current_app.config.get('OLLAMA_BASE_URL')
        if not model:
            model = current_app.config.get('DEFAULT_MODEL')
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if image_b64:
            payload["images"] = [image_b64]
            
        try:
            resp = requests.post(f"{base_url}/api/generate", json=payload)
            if resp.status_code == 200:
                return resp.json().get('response', '')
            return f"Error: {resp.text}"
        except Exception as e:
            return f"Exception: {e}"
