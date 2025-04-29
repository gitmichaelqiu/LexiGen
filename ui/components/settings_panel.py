import tkinter as tk
from tkinter import ttk
from models.translations import get_translation
from models.config import VERSION, DEFAULT_CONFIG

class SettingsPanel(ttk.LabelFrame):
    def __init__(self, parent, language, available_languages, api_service, language_change_callback, main_window):
        super().__init__(parent, text=get_translation(language, "settings"), padding="5")
        self.language = language
        self.api_service = api_service
        self.language_change_callback = language_change_callback
        self.main_window = main_window
        
        # Version Label
        self.version_label = ttk.Label(self, text=f"v{VERSION}", foreground="gray")
        self.version_label.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        # Language Selection
        ttk.Label(self, text=get_translation(language, "language")).grid(row=0, column=1, padx=5)
        self.language_var = tk.StringVar(value=language)
        self.language_select = ttk.Combobox(self, textvariable=self.language_var, 
                                          values=available_languages, state="readonly", width=10)
        self.language_select.grid(row=0, column=2, padx=5)
        self.language_select.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # API URL Entry
        ttk.Label(self, text=get_translation(language, "api_url")).grid(row=0, column=3, padx=5)
        self.api_url_var = tk.StringVar(value=self.api_service.api_url)
        self.api_url_entry = ttk.Entry(self, textvariable=self.api_url_var, width=40)
        self.api_url_entry.grid(row=0, column=4, padx=5)
        
        # Model Selection
        ttk.Label(self, text=get_translation(language, "model")).grid(row=0, column=5, padx=5)
        self.model_var = tk.StringVar(value=self.api_service.model)
        self.model_select = ttk.Combobox(self, textvariable=self.model_var, width=20, state="readonly")
        self.model_select.grid(row=0, column=6, padx=5)
        
        # Status Frame
        self.status_frame = ttk.Frame(self)
        self.status_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        # Status labels
        self.status_labels_frame = ttk.Frame(self.status_frame)
        self.status_labels_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(self.status_labels_frame, text=get_translation(language, "server_status_checking"), foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.status_labels_frame, orient='vertical').pack(side=tk.LEFT, padx=5, fill='y')
        
        self.prompt_status_label = ttk.Label(self.status_labels_frame, text=get_translation(language, "using_default_prompt"), foreground="gray")
        self.prompt_status_label.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        self.buttons_row = ttk.Frame(self.status_frame)
        self.buttons_row.pack(fill=tk.X)
        
        self.check_server_btn = ttk.Button(self.buttons_row, text=get_translation(language, "check_server"), 
                                         command=self.check_server_status)
        self.check_server_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = ttk.Button(self.buttons_row, text=get_translation(language, "setup_help"), 
                                  command=self.open_help)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # Toggle prompt button
        self.toggle_prompt_btn = ttk.Button(self.buttons_row, text=get_translation(language, "toggle_prompt"),
                                          command=self.toggle_prompt)
        self.toggle_prompt_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(self.buttons_row, text=get_translation(language, "check_updates"),
                                   command=lambda: self.main_window.check_for_updates(show_message=True))
        
        # Bind API URL and model changes
        self.api_url_var.trace_add('write', self._on_api_url_change)
        self.model_var.trace_add('write', self._on_model_change)
        
        # Initialize prompt state
        self.using_custom_prompt = False
        self.update_prompt_status()
    
    def _on_language_change(self, event=None):
        new_language = self.language_var.get()
        self.language_change_callback(new_language)
    
    def _on_api_url_change(self, *args):
        """Handle API URL changes and notify parent."""
        self.api_service.api_url = self.api_url_var.get()
        
        # Notify parent window if available
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'on_api_url_change'):
            self.master.master.on_api_url_change(self.api_url_var.get())
    
    def _on_model_change(self, *args):
        """Handle model changes and notify parent."""
        self.api_service.model = self.model_var.get()
        
        # Notify parent window if available
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'on_model_change'):
            self.master.master.on_model_change(self.model_var.get())
    
    def toggle_prompt(self):
        """Toggle between default and custom prompts."""
        self.using_custom_prompt = not self.using_custom_prompt
        
        # Get settings service through API service
        settings_service = self.api_service.settings_service
        
        if self.using_custom_prompt:
            # Check if custom prompts exist in settings.yaml
            custom_generate_prompt = settings_service.settings.get("generate_prompt")
            custom_analysis_prompt = settings_service.settings.get("analysis_prompt")
            
            # Only switch to custom if values exist and are not empty
            if custom_generate_prompt and custom_analysis_prompt:
                # Store current values in settings service
                settings_service.settings["generate_prompt"] = custom_generate_prompt
                settings_service.settings["analysis_prompt"] = custom_analysis_prompt
            else:
                # If no custom prompts, stay on default and don't toggle
                self.using_custom_prompt = False
        else:
            # Switch to default prompts
            settings_service.settings["generate_prompt"] = DEFAULT_CONFIG["generate_prompt"]
            settings_service.settings["analysis_prompt"] = DEFAULT_CONFIG["analysis_prompt"]
        
        # Update the prompt status label
        self.update_prompt_status()
    
    def update_prompt_status(self):
        """Update the prompt status label based on current state."""
        if self.using_custom_prompt:
            self.prompt_status_label.config(
                text=get_translation(self.language, "using_custom_prompt"),
                foreground="green"
            )
        else:
            self.prompt_status_label.config(
                text=get_translation(self.language, "using_default_prompt"),
                foreground="gray"
            )
    
    def check_server_status(self):
        if self.api_service.check_server_status():
            self.status_label.config(
                text=get_translation(self.language, "server_status_connected"),
                foreground="green"
            )
        else:
            self.status_label.config(
                text=get_translation(self.language, "server_status_not_connected"),
                foreground="red"
            )
    
    def update_model_list(self, models):
        self.model_select["values"] = models
        if self.model_var.get() not in models and models:
            self.model_var.set(models[0])
    
    def open_help(self):
        import webbrowser
        webbrowser.open("https://github.com/gitmichaelqiu/LexiGen/blob/main/README.md")
    
    def update_texts(self, language):
        self.language = language
        self.configure(text=get_translation(language, "settings"))
        
        # Update all labels
        for child in self.winfo_children():
            if isinstance(child, ttk.Label):
                text = child.cget("text")
                if text.startswith("v"):  # Version label
                    continue
                # Update specific labels with their translations
                elif "API" in text or "api" in text:
                    child.configure(text=get_translation(language, "api_url"))
                elif "Model" in text.lower():
                    child.configure(text=get_translation(language, "model"))
                elif "Language" in text.lower():
                    child.configure(text=get_translation(language, "language"))

        # Update status label based on current state
        if hasattr(self, 'status_label'):
            if self.api_service.server_connected:
                self.status_label.config(
                    text=get_translation(language, "server_status_connected"),
                    foreground="green"
                )
            else:
                self.status_label.config(
                    text=get_translation(language, "server_status_not_connected"),
                    foreground="red"
                )
        
        # Update prompt status label
        if hasattr(self, 'prompt_status_label'):
            self.update_prompt_status()
        
        # Update buttons
        self.check_server_btn.configure(text=get_translation(language, "check_server"))
        self.help_btn.configure(text=get_translation(language, "setup_help"))
        self.toggle_prompt_btn.configure(text=get_translation(language, "toggle_prompt"))
        
        # Update update button based on current state
        if hasattr(self, 'update_btn'):
            current_text = self.update_btn.cget("text")
            if current_text in ["New version available", "有新版本", get_translation(self.language, "new_version")]:
                self.update_btn.configure(text=get_translation(language, "new_version"))
            elif current_text in ["Up to date", "已是最新", get_translation(self.language, "up_to_date")]:
                self.update_btn.configure(text=get_translation(language, "up_to_date"))
            else:
                self.update_btn.configure(text=get_translation(language, "check_updates"))
    
    def update_update_button(self, status):
        if status == "new_version":
            self.update_btn.configure(text=get_translation(self.language, "new_version"), style="UpdateAvailable.TButton")
        elif status == "up_to_date":
            self.update_btn.configure(text=get_translation(self.language, "up_to_date"), style="UpToDate.TButton")
        else:
            self.update_btn.configure(text=get_translation(self.language, "check_updates"), style="Update.TButton")
        self.update_btn.pack(side=tk.LEFT, padx=5)