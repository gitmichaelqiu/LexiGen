import requests
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from models.config import DEFAULT_CONFIG, get_assets_path
from models.translations import get_translation

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError as e:
    import traceback
    print("llama_cpp import error:", e)
    traceback.print_exc()
    LLAMA_CPP_AVAILABLE = False

class ModelLoadingWindow(tk.Toplevel):
    def __init__(self, parent, model_name, language="English"):
        super().__init__(parent)
        self.parent = parent
        self.title(get_translation(language, "loading_model"))
        
        # Center the window
        width = 300
        height = 100
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Create a progress indicator
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=get_translation(language, "loading_model_message").format(model=model_name)).pack(pady=(0, 10))
        
        progress = ttk.Progressbar(frame, mode="indeterminate", length=200)
        progress.pack()
        progress.start(10)

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
        self.root = None  # Will be set to the root window
        self.is_initial_startup = False  # Flag to track initial startup

    def check_server_status(self, show_message=True, parent_window=None):
        # Check if using "models" as API URL to use local models
        if self.api_url == "models":
            return self._check_local_model_status(show_message, parent_window)
        else:
            # Reset local model flag when not using local mode
            self.using_local_model = False
            if self.local_model is not None:
                del self.local_model
                self.local_model = None
            return self._check_remote_server_status(show_message)
    
    def _check_local_model_status(self, show_message=True, parent_window=None):
        # Check for local models when api_url is set to "models"
        models_dir = os.path.join(get_assets_path(), "models")
        print(models_dir)
        
        # First check if the models directory exists
        if not os.path.exists(models_dir):
            self.server_connected = False
            self.using_local_model = False
            if show_message:
                print("DEBUG: Model Directory Error")
                print(models_dir)
                messagebox.showerror(
                    get_translation(self.language, "server_status_title"),
                    get_translation(self.language, "local_models_dir_error_msg")
                )
            return False

        print("DEBUG: Model Exists")
        
        # Check for available GGUF models
        available_models = [f for f in os.listdir(models_dir) if f.endswith(".gguf") and LLAMA_CPP_AVAILABLE]
        print(os.listdir(models_dir))
        print(LLAMA_CPP_AVAILABLE)
        print(available_models)
        
        if not available_models:
            # No GGUF models available
            print("DEBUG: No GGUF models available")
            self.server_connected = False
            self.using_local_model = False
            if show_message:
                messagebox.showerror(
                    get_translation(self.language, "server_status_title"),
                    get_translation(self.language, "local_models_dir_error_msg")
                )
            return False
            
        # If no model selected but we have models available, set first one as current model
        if not self.model or self.model not in available_models:
            self.model = available_models[0]
            
        # Now we should have a model selected
        if self.model:
            model_path = os.path.join(models_dir, self.model)
            if os.path.exists(model_path) and model_path.endswith(".gguf") and LLAMA_CPP_AVAILABLE:
                # Model exists and is valid
                if show_message and parent_window:
                    # Load with UI feedback
                    loading_window = ModelLoadingWindow(parent_window, self.model, self.language)
                    
                    def load_model_thread():
                        try:
                            # Try to load the model
                            if self.local_model is None or self.local_model.model_path != model_path:
                                # Release previous model if exists
                                if self.local_model is not None:
                                    del self.local_model
                                self.local_model = Llama(model_path=model_path, n_ctx=2048)
                            
                            self.server_connected = True
                            self.using_local_model = True
                            
                            # Close loading window from main thread
                            if loading_window.winfo_exists():
                                loading_window.after(100, loading_window.destroy)
                                
                            # Update UI - first in main window's settings panel
                            if parent_window and hasattr(parent_window, 'update_server_status_display'):
                                parent_window.after(200, parent_window.update_server_status_display)
                            
                            # Then also in the settings panel
                            if hasattr(parent_window, 'settings_panel') and hasattr(parent_window.settings_panel, 'status_label'):
                                parent_window.after(150, lambda: parent_window.settings_panel.status_label.config(
                                    text=get_translation(self.language, "server_status_connected"),
                                    foreground="green"
                                ))
                                
                            if show_message:
                                if parent_window:
                                    # Skip success message during initial startup
                                    if not hasattr(self, 'is_initial_startup') or not self.is_initial_startup:
                                        parent_window.after(200, lambda: messagebox.showinfo(
                                            get_translation(self.language, "server_status_title"),
                                            get_translation(self.language, "local_model_loaded_msg").format(model=self.model)
                                        ))
                        except Exception as e:
                            self.server_connected = False
                            self.using_local_model = False
                            
                            # Close loading window from main thread
                            if loading_window.winfo_exists():
                                loading_window.after(100, loading_window.destroy)
                                
                            # Update UI for failed status
                            if parent_window and hasattr(parent_window, 'update_server_status_display'):
                                parent_window.after(200, parent_window.update_server_status_display)
                            
                            # Then also in the settings panel
                            if hasattr(parent_window, 'settings_panel') and hasattr(parent_window.settings_panel, 'status_label'):
                                parent_window.after(150, lambda: parent_window.settings_panel.status_label.config(
                                    text=get_translation(self.language, "server_status_not_connected"),
                                    foreground="red"
                                ))
                                
                            if show_message:
                                if parent_window:
                                    parent_window.after(200, lambda: messagebox.showerror(
                                        get_translation(self.language, "server_status_title"),
                                        get_translation(self.language, "local_model_error_msg").format(error=str(e))
                                    ))
                    
                    # Start loading thread
                    thread = threading.Thread(target=load_model_thread)
                    thread.daemon = True
                    thread.start()
                    return True
                else:
                    # Load without UI feedback (silent)
                    try:
                        if self.local_model is None or self.local_model.model_path != model_path:
                            if self.local_model is not None:
                                del self.local_model
                            self.local_model = Llama(model_path=model_path, n_ctx=2048)
                        
                        self.server_connected = True
                        self.using_local_model = True
                        return True
                    except Exception as e:
                        self.server_connected = False
                        self.using_local_model = False
                        if show_message:
                            messagebox.showerror(
                                get_translation(self.language, "server_status_title"),
                                get_translation(self.language, "local_model_error_msg").format(error=str(e))
                            )
                        return False
            else:
                # Model file doesn't exist or isn't valid
                self.server_connected = False
                self.using_local_model = False
                if show_message:
                    messagebox.showerror(
                        get_translation(self.language, "server_status_title"),
                        get_translation(self.language, "local_model_not_found_msg").format(model=self.model)
                    )
                return False
        else:
            # This shouldn't happen given our logic above
            self.server_connected = False
            self.using_local_model = False
            if show_message:
                messagebox.showerror(
                    get_translation(self.language, "server_status_title"),
                    get_translation(self.language, "local_models_dir_error_msg")
                )
            return False
    
    def _check_remote_server_status(self, show_message=True):
        # If not using local model, check remote server
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
        # If using local models, only show local models
        if self.api_url == "models":
            models_dir = os.path.join(get_assets_path(), "models")
            local_models = []
            
            if os.path.exists(models_dir):
                for file in os.listdir(models_dir):
                    if file.endswith(".gguf") and LLAMA_CPP_AVAILABLE:
                        local_models.append(file)
            
            if local_models:
                self.available_models = local_models
                return True
            else:
                self.available_models = []
                return False
        else:
            # Using remote server, fetch models from API
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
