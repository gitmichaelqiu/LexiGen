import requests
from tkinter import messagebox
from models.config import DEFAULT_CONFIG
from models.translations import get_translation

class APIService:
    def __init__(self, language="English", api_url=None, settings_service=None):
        self.language = language
        self.settings_service = settings_service
        if self.settings_service:
            self.api_url = api_url if api_url else self.settings_service.get_settings("api_url")
            self.model = self.settings_service.get_settings("model")
        else:
            self.api_url = api_url
            self.model = None
        self.server_connected = False
        self.available_models = []

    def check_server_status(self, show_message=True):
        try:
            response = requests.get(self.api_url.replace("/generate", "/version"))
            if response.status_code == 200:
                self.server_connected = True
                if show_message:
                    version = response.json().get('version', 'Unknown')
                    messagebox.showinfo(
                        get_translation(self.language, "server_status_title"),
                        get_translation(self.language, "server_connected_msg").format(version=version)
                    )
                return True
            else:
                self.server_connected = False
                if show_message:
                    messagebox.showerror(
                        get_translation(self.language, "server_status_title"),
                        get_translation(self.language, "server_error_msg")
                    )
                return False
        except Exception as e:
            self.server_connected = False
            if show_message:
                messagebox.showerror(
                    get_translation(self.language, "server_status_title"),
                    get_translation(self.language, "server_connection_error_msg").format(error=str(e))
                )
            return False

    def fetch_models(self):
        try:
            response = requests.get(self.api_url.replace("/generate", "/tags"))
            if response.status_code == 200:
                models = response.json()
                self.available_models = [model["name"] for model in models["models"]]
                if not self.available_models:
                    self.available_models = ["llama2"]
                return True
        except Exception:
            self.available_models = ["llama2"]
            return False

    def generate_sentence(self, word, prompt_template):
        if not self.server_connected:
            messagebox.showerror(
                "Server Error",
                get_translation(self.language, "server_connection_guide")
            )
            return None
        
        prompt = prompt_template.format(word=word)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    self.api_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                sentence = result["response"].strip()
                
                word_variations = {word.lower(), word.capitalize(), word.upper()}
                if any(variation in sentence.lower() for variation in word_variations):
                    return sentence
                
                if attempt == max_attempts - 1:
                    return sentence
                
            except requests.exceptions.RequestException as e:
                messagebox.showerror(
                    "Error", 
                    get_translation(self.language, "generation_error_msg").format(error=str(e))
                )
                return None
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    get_translation(self.language, "unexpected_error_msg").format(error=str(e))
                )
                return None
        
        return None
