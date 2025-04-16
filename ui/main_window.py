import tkinter as tk
from tkinter import ttk, scrolledtext
from models.config import VERSION, DEFAULT_CONFIG
from models.translations import load_translations, get_translation
from models.word_processor import WordProcessor
from services.api_service import APIService
from services.document_service import DocumentService
from services.update_service import UpdateService
from services.settings_service import SettingsService
from ui.components.sentence_widget import SentenceWidgetManager
from ui.components.settings_panel import SettingsPanel
import os
import sys

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(f"LexiGen v{VERSION} - Fill-in-the-Blank Generator")
        self.root.geometry("1100x800")
        
        # Initialize settings service
        self.settings_service = SettingsService()
        
        # Initialize services with settings from service
        self.language = self.settings_service.get_setting("language", DEFAULT_CONFIG["language"])
        self.word_processor = WordProcessor(self.language)
        
        # Get API URL from settings
        api_url = self.settings_service.get_setting("api_url", DEFAULT_CONFIG["api_url"])
        self.api_service = APIService(self.language, api_url)
        
        # Get model from settings
        model = self.settings_service.get_setting("model", DEFAULT_CONFIG["model"])
        self.api_service.model = model
        
        self.document_service = DocumentService(self.language)
        self.update_service = UpdateService(self.language)
        
        # Load translations
        self.available_languages = load_translations()
        
        # Setup UI
        self.setup_ui()
        
        # Immediately check server status (not waiting for the scheduled checks)
        self.api_service.check_server_status(show_message=False)
        
        # Setup close handler to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initial setup (scheduled to run after UI is ready)
        self.root.after(100, self.initial_setup)
        self.root.after(200, lambda: self.check_for_updates(show_message=False))
        
    def setup_ui(self):
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create settings panel
        self.settings_panel = SettingsPanel(
            self.main_container,
            self.language,
            self.available_languages,
            self.api_service,
            self.on_language_change
        )
        self.settings_panel.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Input Frame
        self.input_frame = ttk.LabelFrame(self.main_container, text=get_translation(self.language, "input_words"), padding="5")
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Word Input
        self.word_input = scrolledtext.ScrolledText(self.input_frame, height=3, width=70)
        self.word_input.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.words_label = ttk.Label(self.input_frame, text=get_translation(self.language, "enter_words"))
        self.words_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Buttons Frame for Generate and Append
        buttons_frame = ttk.Frame(self.input_frame)
        buttons_frame.grid(row=1, column=1, sticky=tk.E, padx=5)
        
        self.generate_btn = ttk.Button(buttons_frame, text=get_translation(self.language, "generate"), 
                                     command=lambda: self.generate_sentences(append=False))
        self.append_btn = ttk.Button(buttons_frame, text=get_translation(self.language, "append"), 
                                   command=lambda: self.generate_sentences(append=True))
        
        # Initially only show generate button and ensure append is disabled
        self.generate_btn.pack(side=tk.LEFT)
        self.append_btn.configure(state="disabled")  # Explicitly disable the append button
        self.append_btn.pack_forget()
        
        # Progress Bar
        self.progress_frame = ttk.Frame(self.input_frame)
        self.progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text=get_translation(self.language, "generating"))
        self.progress_label.pack(side=tk.LEFT, padx=(0, 5))
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_frame.grid_remove()
        
        # Sentences Frame
        self.sentence_manager = SentenceWidgetManager(
            self.main_container,
            self.language,
            self.word_processor,
            self.api_service,
            self.on_sentences_changed
        )
        self.sentence_manager.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(2, weight=1)
        
    def initial_setup(self):
        # Use already checked server status
        server_connected = self.api_service.server_connected
        
        # If server is connected, fetch available models
        if server_connected:
            self.api_service.fetch_models()
            self.settings_panel.update_model_list(self.api_service.available_models)
            
            # Check if we have sentences before enabling the append button
            has_sentences = len(self.sentence_manager.sentence_widgets) > 0
            if has_sentences:
                self.append_btn.pack(side=tk.LEFT, padx=(5, 0))
                self.append_btn.configure(state="normal")
            else:
                # Make sure append button is disabled
                self.append_btn.configure(state="disabled")
        else:
            # Make sure append button is disabled when server is not connected
            self.append_btn.configure(state="disabled")
        
        # Always update the status display, regardless of connection state
        if server_connected:
            self.settings_panel.status_label.config(
                text=get_translation(self.language, "server_status_connected"),
                foreground="green"
            )
        else:
            self.settings_panel.status_label.config(
                text=get_translation(self.language, "server_status_not_connected"),
                foreground="red"
            )
    
    def on_language_change(self, new_language):
        self.language = new_language
        self.api_service.language = new_language
        self.document_service.language = new_language
        self.update_service.language = new_language
        self.word_processor.language = new_language
        self.update_ui_texts()
        
        # Save language setting
        self.settings_service.set_setting("language", new_language)
    
    def update_ui_texts(self):
        self.input_frame.configure(text=get_translation(self.language, "input_words"))
        self.words_label.configure(text=get_translation(self.language, "enter_words"))
        self.generate_btn.configure(text=get_translation(self.language, "generate"))
        self.append_btn.configure(text=get_translation(self.language, "append"))
        self.progress_label.configure(text=get_translation(self.language, "generating"))
        
        self.settings_panel.update_texts(self.language)
        self.sentence_manager.update_texts(self.language)
    
    def generate_sentences(self, append=False):
        words = [word.strip().lower() for word in self.word_input.get("1.0", tk.END).strip().split(",")]
        words = [w for w in words if w]
        
        if not words:
            return
        
        if not append:
            self.sentence_manager.clear_sentences()
            
        self.word_input.delete("1.0", tk.END)
        self.progress_bar['maximum'] = len(words)
        self.progress_bar['value'] = 0
        self.progress_frame.grid()
        self.generate_btn.configure(state="disabled")
        
        if hasattr(self, 'append_btn'):
            self.append_btn.configure(state="disabled")
        
        self.root.update()
        
        sentences_generated = 0
        
        for i, word in enumerate(words):
            sentence = self.api_service.generate_sentence(word, DEFAULT_CONFIG["default_prompt"])
            if sentence:
                self.sentence_manager.add_sentence(word, sentence)
                sentences_generated += 1
            else:
                self.progress_frame.grid_remove()
                return
            
            self.progress_bar['value'] = i + 1
            self.progress_label.configure(text=f"{get_translation(self.language, 'generating')} ({i + 1}/{len(words)})")
            self.root.update()
        
        self.progress_frame.grid_remove()
        if self.api_service.server_connected:
            self.generate_btn.configure(state="normal")
            
            # Show append button after successful generation
            if sentences_generated > 0:
                if hasattr(self, 'append_btn'):
                    self.append_btn.pack(side=tk.LEFT, padx=(5, 0))
                    self.append_btn.configure(state="normal")
    
    def check_for_updates(self, show_message=True):
        result = self.update_service.check_for_updates(show_message)
        self.settings_panel.update_update_button(result)

    def on_sentences_changed(self, has_sentences):
        """Called when sentences are added or removed."""
        if hasattr(self, 'append_btn'):
            if has_sentences and self.api_service.server_connected:
                self.append_btn.configure(state="normal")
                # Make sure it's visible when it should be
                if not self.append_btn.winfo_ismapped():
                    self.append_btn.pack(side=tk.LEFT, padx=(5, 0))
            else:
                self.append_btn.configure(state="disabled")

    def on_api_url_change(self, new_url):
        """Called when API URL is changed."""
        self.api_service.api_url = new_url
        self.settings_service.set_setting("api_url", new_url)
    
    def on_model_change(self, new_model):
        """Called when model is changed."""
        self.api_service.model = new_model
        self.settings_service.set_setting("model", new_model)
    
    def on_close(self):
        """Save settings before closing the application."""
        self.settings_service.save_settings()
        self.root.destroy()