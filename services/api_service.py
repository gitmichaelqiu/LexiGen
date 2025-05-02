import requests
import os
from tkinter import messagebox
from models.config import DEFAULT_CONFIG, get_assets_path
from models.translations import get_translation
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

class APIService:
    def __init__(self, language="English", api_url=None, settings_service=None, word_processor=None):
        self.language = language
        self.settings_service = settings_service
        if self.settings_service:
            self.api_url = api_url if api_url else self.settings_service.get_settings("api_url")
            self.model = self.settings_service.get_settings("model")
        else:
            self.api_url = api_url
            self.model = None
        self.server_connected = False
        self.word_processor = word_processor
        self.available_models = []
        self.local_model = None
        self.using_local_model = False

    def check_server_status(self, show_message=True):
        # First check if the model is a local GGUF file
        models_dir = os.path.join(get_assets_path(), "models")
        if os.path.exists(models_dir) and self.model:
            model_path = os.path.join(models_dir, self.model)
            if os.path.exists(model_path) and model_path.endswith(".gguf") and LLAMA_CPP_AVAILABLE:
                try:
                    # Try to load the model
                    if self.local_model is None or self.local_model.model_path != model_path:
                        # Release previous model if exists
                        if self.local_model is not None:
                            del self.local_model
                        self.local_model = Llama(model_path=model_path, n_ctx=2048)
                    
                    self.server_connected = True
                    self.using_local_model = True
                    
                    if show_message:
                        messagebox.showinfo(
                            get_translation(self.language, "server_status_title"),
                            get_translation(self.language, "server_connected_msg").format(version=f"Local model: {self.model}")
                        )
                    return True
                except Exception as e:
                    self.server_connected = False
                    self.using_local_model = False
                    if show_message:
                        messagebox.showerror(
                            get_translation(self.language, "server_status_title"),
                            get_translation(self.language, "server_connection_error_msg").format(error=str(e))
                        )
                    return False
        
        # If not using local model, check remote server
        self.using_local_model = False
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
        # Add local models to the list
        models_dir = os.path.join(get_assets_path(), "models")
        local_models = []
        
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith(".gguf") and LLAMA_CPP_AVAILABLE:
                    local_models.append(file)
        
        # If using local models, just return those
        if local_models:
            self.available_models = local_models
            return True
            
        # Otherwise try to fetch from server
        try:
            response = requests.get(self.api_url.replace("/generate", "/tags"))
            if response.status_code == 200:
                models = response.json()
                remote_models = [model["name"] for model in models["models"]]
                if remote_models:
                    if local_models:
                        # Combine both lists if we have both
                        self.available_models = local_models + remote_models
                    else:
                        self.available_models = remote_models
                    return True
        except Exception:
            pass
            
        # Fallback if we have local models but server fetch failed
        if local_models:
            self.available_models = local_models
            return True
            
        # Final fallback
        self.available_models = ["llama2"]
        return False

    def generate_sentence(self, word, prompt_template):
        if not self.server_connected:
            messagebox.showerror(
                get_translation(self.language, "server_error_title"),
                get_translation(self.language, "server_connection_guide")
            )
            return None

        prompt = prompt_template.format(word=word)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if self.using_local_model and self.local_model is not None:
                    # Use local model for generation
                    output = self.local_model(
                        prompt,
                        max_tokens=256,
                        stop=["</s>", "\n\n"],
                        echo=False
                    )
                    sentence = output['choices'][0]['text'].strip()
                else:
                    # Use remote API
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

                # Use stem to verify the sentence
                sentence_split = sentence.split()
                sentence_stems = []
                for sentence_fragment in sentence_split:
                    sentence_stems.append(self.word_processor.get_word_stem(sentence_fragment))
                if self.word_processor.get_word_stem(word.lower()) in sentence_stems:
                    return sentence
                
                if attempt == max_attempts - 1:
                    return sentence
                
            except requests.exceptions.RequestException as e:
                if self.using_local_model:
                    # If using local model, this is unexpected
                    messagebox.showerror(
                        get_translation(self.language, "error_title"), 
                        get_translation(self.language, "unexpected_error_msg").format(error=str(e))
                    )
                else:
                    messagebox.showerror(
                        get_translation(self.language, "error_title"), 
                        get_translation(self.language, "generation_error_msg").format(error=str(e))
                    )
                return None
            except Exception as e:
                messagebox.showerror(
                    get_translation(self.language, "error_title"), 
                    get_translation(self.language, "unexpected_error_msg").format(error=str(e))
                )
                return None
        
        return None
