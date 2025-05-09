import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from models.config import VERSION, DEFAULT_CONFIG, get_assets_path
from models.translations import load_translations, get_translation
from models.word_processor import WordProcessor
from services.api_service import APIService, ModelLoadingWindow
from services.document_service import DocumentService
from services.update_service import UpdateService
from services.settings_service import SettingsService
from ui.components.sentence_widget import SentenceWidgetManager
from ui.components.settings_panel import SettingsPanel
from services.icon_service import create_icon
import os
import sys
import ctypes
import threading

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("LexiGen")
        
        # Flag to track initial startup
        self.is_initial_startup = True

        width = 1100
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        if sys.platform == 'win32':
            # Add window icon
            try:
                create_icon()
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'Lexi.ico')
                self.root.iconbitmap(icon_path)
            except Exception as e:
                pass
            
            # Adjust dpi
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
                root.tk.call('tk', 'scaling', ScaleFactor/75)
            except Exception:
                pass

        # Initialize settings service
        self.settings_service = SettingsService()
        
        # Initialize services with settings from service
        self.language = self.settings_service.get_setting("language", self.settings_service.get_settings("language"))
        self.word_processor = WordProcessor(self.language)
        
        # Get API URL and model from settings
        api_url = self.settings_service.get_setting("api_url", self.settings_service.get_settings("api_url"))
        self.api_service = APIService(self.language, api_url, self.settings_service, self.word_processor)
        self.api_service.root = self.root  # Set root window reference
        model = self.settings_service.get_setting("model", self.settings_service.get_settings("model"))
        self.api_service.model = model
        
        self.document_service = DocumentService(self.language)
        self.update_service = UpdateService(self.language)
        # Set root window for the update service
        self.update_service.set_root(self.root)
        
        self.context = None

        # Load translations
        self.available_languages = load_translations()
        
        # Setup UI
        self.setup_ui()
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Create a loading window first if using local models
        if api_url == "models":
            # Check models directory to see if we have models to load
            models_dir = os.path.join(get_assets_path(), "models")
            available_models = []
            
            if os.path.exists(models_dir):
                for file in os.listdir(models_dir):
                    if file.endswith(".gguf"):
                        available_models.append(file)
            
            # Only show loading window if we have models to load
            if available_models:
                selected_model = model if model in available_models else available_models[0]
                # Don't create a separate loading window here, let the check_server_status function handle it
                
                # Check server status which will load the model in background and show its own loading window
                # Pass the initial startup flag to control success message display
                self.api_service.is_initial_startup = self.is_initial_startup
                self.api_service.check_server_status(show_message=True, parent_window=self.root)
                
                # Schedule initial setup after a delay to ensure model loading is complete
                self.root.after(1000, self.initial_setup)
                self.root.after(1200, lambda: self.check_for_updates(show_message=False))
            else:
                # No models to load, just check server status normally
                self.api_service.check_server_status(show_message=False, parent_window=None)
                self.root.after(100, self.initial_setup)
                self.root.after(200, lambda: self.check_for_updates(show_message=False))
        else:
            # For remote API, check server status without loading window
            self.api_service.check_server_status(show_message=False, parent_window=None)
            self.root.after(100, self.initial_setup)
            self.root.after(200, lambda: self.check_for_updates(show_message=False))
        
        # Reset the initial startup flag after the application is fully loaded
        self.root.after(1500, self._reset_initial_startup_flag)
        
        # Setup close handler to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for various actions"""
        # Get platform-specific modifier key
        modifier = "Command" if sys.platform == "darwin" else "Control"
        
        # Bind Enter in word input to append/generate
        self.word_input.bind("<Return>", self._handle_enter_key)
        
        # Bind Ctrl/Cmd + Enter to generate
        self.root.bind(f"<{modifier}-Return>", lambda event: self.generate_sentences(append=False))
        
        # Bind Ctrl/Cmd + E to export
        self.root.bind(f"<{modifier}-e>", lambda event: self.sentence_manager.export_docx())
        
        # Bind Ctrl/Cmd + S to save history
        self.root.bind(f"<{modifier}-s>", lambda event: self.sentence_manager.save_history())
        
        # Bind Ctrl/Cmd + O to load history
        self.root.bind(f"<{modifier}-o>", lambda event: self.sentence_manager.load_history())
        
        # Bind Ctrl/Cmd + / to show/hide all
        self.root.bind(f"<{modifier}-slash>", lambda event: self.sentence_manager.show_all_words())
        
        # Bind Ctrl/Cmd + T to toggle context window
        self.root.bind(f"<{modifier}-t>", self._toggle_context_window)
    
    def _handle_enter_key(self, event):
        """Handle Enter key in word input - append or generate based on sentences state"""
        # Check if there are sentences already
        has_sentences = len(self.sentence_manager.sentence_widgets) > 0
        
        if has_sentences:
            # If there are sentences, append
            self.generate_sentences(append=True)
        else:
            # If no sentences, generate
            self.generate_sentences(append=False)
        
        # Prevent default behavior
        return "break"
        
    def setup_ui(self):
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create settings panel
        self.settings_panel = SettingsPanel(
            self.main_container,
            self.language,
            self.available_languages,
            self.api_service,
            self.on_language_change,
            self
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
        
        self.context_btn = ttk.Button(buttons_frame, text=get_translation(self.language, "context_button"),
                                    command=self._show_context_dialog)
        self.generate_btn = ttk.Button(buttons_frame, text=get_translation(self.language, "generate"), 
                                     command=lambda: self.generate_sentences(append=False))
        self.append_btn = ttk.Button(buttons_frame, text=get_translation(self.language, "append"), 
                                   command=lambda: self.generate_sentences(append=True))
        
        # Initially only show context and generate buttons
        self.context_btn.pack(side=tk.LEFT)
        self.generate_btn.pack(side=tk.LEFT, padx=(5, 0))
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
            self.on_sentences_changed,
            self
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
        
        # Check server status after language change
        self.api_service.check_server_status(show_message=False, parent_window=self.root)
        self.update_server_status_display()
        
        # Rebind keyboard shortcuts after language change
        self._setup_keyboard_shortcuts()
    
    def update_ui_texts(self):
        self.input_frame.configure(text=get_translation(self.language, "input_words"))
        self.words_label.configure(text=get_translation(self.language, "enter_words"))
        self.generate_btn.configure(text=get_translation(self.language, "generate"))
        self.append_btn.configure(text=get_translation(self.language, "append"))
        self.context_btn.configure(text=get_translation(self.language, "context_button"))
        self.progress_label.configure(text=get_translation(self.language, "generating"))
        
        self.settings_panel.update_texts(self.language)
        self.sentence_manager.update_texts(self.language)
    
    def generate_sentences(self, append=False):
        # Get prompt from settings, fallback to default if None
        prompt = self.settings_service.get_settings("generation_prompt")

        if r'{word}' not in prompt:
            messagebox.showerror(
                get_translation(self.language, "error_title"),
                get_translation(self.language, "invalid_prompt_format")
            )
            return

        words = [word.strip().lower() for word in self.word_input.get("1.0", tk.END).strip().split(",")]
        words = [w for w in words if w]
        
        if not words:
            return
        
        if not append:
            self.sentence_manager.clear_sentences()
            
        self.word_input.delete("1.0", tk.END)
        
        # Reset progress bar and label
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(words)
        self.progress_label.configure(text=get_translation(self.language, "generating"))
        self.progress_frame.grid()
        self.generate_btn.configure(state="disabled")
        
        if hasattr(self, 'append_btn'):
            self.append_btn.configure(state="disabled")
        
        self.root.update()
        
        sentences_generated = 0
        
        for i, word in enumerate(words):
            # Add context to prompt if available
            current_prompt = prompt
            if hasattr(self, 'context') and self.context:
                context_attachment_prompt = self.settings_service.get_settings("context_attachment_prompt")

                if r'{context}' not in context_attachment_prompt:
                    messagebox.showerror(
                        get_translation(self.language, "error_title"),
                        get_translation(self.language, "invalid_prompt_format")
                    )
                    return

                current_prompt = context_attachment_prompt.format(context=self.context) + "\n" + prompt
            
            sentence = self.api_service.generate_sentence(word, current_prompt)
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
        result = self.update_service.check_for_updates(show_message, auto_update=True)
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
        # Update API service (already done in the settings panel)
        # self.api_service.api_url = new_url
        
        # Save immediately to settings only if it's one of the default options
        # or already exists in settings (non-default custom URL)
        current_api_url = self.settings_service.get_setting("api_url")
        default_urls = ["http://127.0.0.1:11434/api/generate", "models"]
        
        if new_url in default_urls or new_url == current_api_url:
            self.settings_service.set_setting("api_url", new_url)
        
        # No need to check server status here - already done in settings panel
        # self.root.after(100, lambda: self.api_service.check_server_status(show_message=False, parent_window=self.root))
        self.root.after(100, lambda: self.update_server_status_display())

    def on_model_change(self, new_model):
        """Called when model is changed."""
        # Update API service (already done in the settings panel)
        # self.api_service.model = new_model
        
        # Save immediately to settings
        self.settings_service.set_setting("model", new_model)
        
        # No need to check server status here - already done in settings panel
        # self.root.after(100, lambda: self.api_service.check_server_status(show_message=False, parent_window=self.root))
        self.root.after(100, lambda: self.update_server_status_display())

    def update_server_status_display(self):
        """Update the server status display to reflect current state."""
        if self.api_service.server_connected:
            self.settings_panel.status_label.config(
                text=get_translation(self.language, "server_status_connected"),
                foreground="green"
            )
        else:
            self.settings_panel.status_label.config(
                text=get_translation(self.language, "server_status_not_connected"),
                foreground="red"
            )
    
    def on_close(self):
        """Save all current settings before closing the application."""
        # Ensure we save the most up-to-date settings
        # For API URL, only save if it's one of the defaults or an existing custom URL
        current_api_url = self.settings_service.get_setting("api_url")
        default_urls = ["http://127.0.0.1:11434/api/generate", "models"]
        
        settings_to_save = {"language": self.language}
        
        # Only update API URL if it's a default one or matches the existing custom URL
        if self.api_service.api_url in default_urls or self.api_service.api_url == current_api_url:
            settings_to_save["api_url"] = self.api_service.api_url
        
        # Always save the model
        settings_to_save["model"] = self.api_service.model
        
        # Update all settings at once
        self.settings_service.update_settings(settings_to_save)
        
        # Final save
        self.settings_service.save_settings()
        self.root.destroy()

    def _toggle_context_window(self, event=None):
        """Toggle the context window - open if closed, save and close if open."""
        if hasattr(self, '_context_dialog') and self._context_dialog.winfo_exists():
            # Window is open, save and close it
            self._save_context()
            self._context_dialog.destroy()
        else:
            # Window is not open, open it
            self._show_context_dialog()
    
    def _show_context_dialog(self):
        """Show dialog for entering context."""
        self._context_dialog = tk.Toplevel(self.root)
        self._context_dialog.title(get_translation(self.language, "context"))
        width = 500
        height = 300
        x = (self._context_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self._context_dialog.winfo_screenheight() // 2) - (height // 2)
        self._context_dialog.geometry(f"{width}x{height}+{x}+{y}")
        self._context_dialog.transient(self.root)
        self._context_dialog.grab_set()

        # Bind Ctrl/Cmd + T to save and close
        modifier = "Command" if sys.platform == "darwin" else "Control"
        self._context_dialog.bind(f"<{modifier}-t>", lambda e: self._save_context())
        
        # Create main frame
        main_frame = ttk.Frame(self._context_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Context label and text widget
        ttk.Label(main_frame, text=get_translation(self.language, "enter_context")).pack(anchor=tk.W)
        self._context_text = scrolledtext.ScrolledText(main_frame, height=5, width=40)
        self._context_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Load existing context if any
        if hasattr(self, 'context') and self.context:
            self._context_text.insert("1.0", self.context)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text=get_translation(self.language, "save"), 
                  command=self._save_context).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text=get_translation(self.language, "cancel"), 
                  command=self._context_dialog.destroy).pack(side=tk.RIGHT)
    
    def _save_context(self, event=None):
        """Save the current context and close the dialog."""
        if hasattr(self, '_context_text') and self._context_text.winfo_exists():
            context = self._context_text.get("1.0", tk.END).strip()
            if context:
                self.context = context
            else:
                self.context = None
            if hasattr(self, '_context_dialog') and self._context_dialog.winfo_exists():
                self._context_dialog.destroy()
        return "break"  # Prevent the event from propagating

    def _reset_initial_startup_flag(self):
        """Reset the initial startup flag after application is loaded."""
        self.is_initial_startup = False
        if hasattr(self.api_service, 'is_initial_startup'):
            self.api_service.is_initial_startup = False
