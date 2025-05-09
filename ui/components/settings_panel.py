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
        
        # Define default API URL options
        self.DEFAULT_API_URLS = ["http://127.0.0.1:11434/api/generate", "GGUF Models"]
        
        # Version Label
        self.version_label = ttk.Label(self, text=f"v{VERSION}", foreground="gray")
        self.version_label.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        # Language Selection
        self.language_label = ttk.Label(self, text=get_translation(language, "language"))
        self.language_label.grid(row=0, column=1, padx=5)
        self.language_var = tk.StringVar(value=language)
        self.language_select = ttk.Combobox(self, textvariable=self.language_var, 
                                          values=available_languages, state="readonly", width=10)
        self.language_select.grid(row=0, column=2, padx=5)
        self.language_select.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # API URL Entry with dropdown
        self.api_url_label = ttk.Label(self, text=get_translation(language, "api_url"))
        self.api_url_label.grid(row=0, column=3, padx=5)
        self.api_url_var = tk.StringVar(value=self._get_display_api_url())
        
        # Determine dropdown options - always include defaults and add current if it's different
        self.api_url_options = self.DEFAULT_API_URLS.copy()
        current_api_url = self.api_service.api_url
        # If the current URL is "models", display it as "GGUF Models"
        display_url = "GGUF Models" if current_api_url == "models" else current_api_url
        
        # Add the current URL to options if it's not one of the defaults
        if display_url not in self.api_url_options:
            self.api_url_options.append(display_url)
        
        self.api_url_entry = ttk.Combobox(self, textvariable=self.api_url_var, width=40, 
                                         values=self.api_url_options, state="readonly")
        self.api_url_entry.grid(row=0, column=4, padx=5)
        
        # Model Selection
        self.model_label = ttk.Label(self, text=get_translation(language, "model"))
        self.model_label.grid(row=0, column=5, padx=5)
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
        display_url = self.api_url_var.get()
        internal_url = self._get_internal_api_url(display_url)
        
        # Set the actual backend value
        self.api_service.api_url = internal_url
        
        # Always check server status and update models when API URL changes
        # First clear the current model list
        self.model_select["values"] = []
        self.status_label.config(
            text=get_translation(self.language, "server_status_checking"),
            foreground="gray"
        )
        self.update()
        
        # Fetch models first, before checking server status
        self.api_service.fetch_models()
        self.update_model_list(self.api_service.available_models)
        
        # For GGUF Models, we need to select a model first before checking server
        if internal_url == "models" and self.api_service.available_models:
            # Only set the model if it's not already set or not in the available models
            if (not self.model_var.get() or 
                self.model_var.get() not in self.api_service.available_models):
                self.model_var.set(self.api_service.available_models[0])
        
        # Now check server status (after model selection for GGUF Models)
        server_status = self.api_service.check_server_status(show_message=False, parent_window=self.main_window.root)
        
        # Update status display
        if server_status:
            self.status_label.config(
                text=get_translation(self.language, "server_status_connected"),
                foreground="green"
            )
        else:
            self.status_label.config(
                text=get_translation(self.language, "server_status_not_connected"),
                foreground="red"
            )
        
        # Notify parent window if available
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'on_api_url_change'):
            self.master.master.on_api_url_change(internal_url)
    
    def _on_model_change(self, *args):
        """Handle model changes and notify parent."""
        if not self.model_var.get():
            return  # Don't process empty model selections
            
        self.api_service.model = self.model_var.get()
        
        # If using local models (GGUF), check server status to load the model
        if self.api_service.api_url == "models":
            # Update status to checking
            self.status_label.config(
                text=get_translation(self.language, "server_status_checking"),
                foreground="gray"
            )
            self.update()
            
            # Check server (which will load the model)
            server_status = self.api_service.check_server_status(
                show_message=False, 
                parent_window=self.main_window.root
            )
            
            # Update status display
            if server_status:
                self.status_label.config(
                    text=get_translation(self.language, "server_status_connected"),
                    foreground="green"
                )
            else:
                self.status_label.config(
                    text=get_translation(self.language, "server_status_not_connected"),
                    foreground="red"
                )
        
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
            custom_generation_prompt = settings_service.external_generation_prompt
            custom_analysis_prompt = settings_service.external_analysis_prompt
            custom_tense_prompt = settings_service.external_tense_prompt
            custom_analysis_tense_prompt = settings_service.external_analysis_tense_prompt
            custom_context_attachment_prompt = settings_service.external_context_attachment_prompt
            
            # Only switch to custom if values exist and are not empty
            if custom_generation_prompt or custom_analysis_prompt or custom_tense_prompt or custom_analysis_tense_prompt or custom_context_attachment_prompt:
                # Store current values in settings service
                settings_service.settings["generation_prompt"] = custom_generation_prompt if custom_generation_prompt else DEFAULT_CONFIG["generation_prompt"]
                settings_service.settings["analysis_prompt"] = custom_analysis_prompt if custom_analysis_prompt else DEFAULT_CONFIG["analysis_prompt"]
                settings_service.settings["tense_prompt"] = custom_tense_prompt if custom_tense_prompt else DEFAULT_CONFIG["tense_prompt"]
                settings_service.settings["analysis_tense_prompt"] = custom_analysis_tense_prompt if custom_analysis_tense_prompt else DEFAULT_CONFIG["analysis_tense_prompt"]
                settings_service.settings["context_attachment_prompt"] = custom_context_attachment_prompt if custom_context_attachment_prompt else DEFAULT_CONFIG["context_attachment_prompt"]
            else:
                # If no custom prompts, stay on default and don't toggle
                self.using_custom_prompt = False
        else:
            # Switch to default prompts
            settings_service.settings["generation_prompt"] = DEFAULT_CONFIG["generation_prompt"]
            settings_service.settings["analysis_prompt"] = DEFAULT_CONFIG["analysis_prompt"]
            settings_service.settings["tense_prompt"] = DEFAULT_CONFIG["tense_prompt"]
            settings_service.settings["analysis_tense_prompt"] = DEFAULT_CONFIG["analysis_tense_prompt"]
            settings_service.settings["context_attachment_prompt"] = DEFAULT_CONFIG["context_attachment_prompt"]
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
        if self.api_service.check_server_status(parent_window=self.main_window.root):
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
        webbrowser.open("https://gitmichaelqiu.github.io/my-projects/lexigen/lexigen/")
    
    def update_texts(self, language):
        self.language = language
        self.configure(text=get_translation(language, "settings"))
        
        # Update the main labels directly
        self.language_label.configure(text=get_translation(language, "language"))
        self.api_url_label.configure(text=get_translation(language, "api_url"))
        self.model_label.configure(text=get_translation(language, "model"))
        
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
        
        # Update direct update button if present
        if hasattr(self, 'direct_update_btn'):
            self.direct_update_btn.configure(text=get_translation(language, "update_now_title"))
        
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
            # When a new version is available, show only the direct update button
            
            # If the normal update button exists, hide it
            if hasattr(self, 'update_btn') and self.update_btn.winfo_ismapped():
                self.update_btn.pack_forget()
            
            # Add a direct update button if not already present
            if not hasattr(self, 'direct_update_btn'):
                self.direct_update_btn = ttk.Button(
                    self.buttons_row, 
                    text=get_translation(self.language, "update_now_title"),
                    command=self._direct_update,
                    style="UpdateAvailable.TButton"
                )
                self.direct_update_btn.pack(side=tk.LEFT, padx=5)
        elif status == "up_to_date":
            # Change the regular update button to show it's up to date
            self.update_btn.configure(
                text=get_translation(self.language, "up_to_date"), 
                style="UpToDate.TButton"
            )
            # Remove direct update button if it exists
            self._remove_direct_update_btn()
            
            # Make sure the regular update button is visible
            if hasattr(self, 'update_btn') and not self.update_btn.winfo_ismapped():
                self.update_btn.pack(side=tk.LEFT, padx=5)
        else:
            # Change back to regular check for updates button
            self.update_btn.configure(
                text=get_translation(self.language, "check_updates"), 
                style="Update.TButton"
            )
            # Remove direct update button if it exists
            self._remove_direct_update_btn()
            
            # Make sure the regular update button is visible
            if hasattr(self, 'update_btn') and not self.update_btn.winfo_ismapped():
                self.update_btn.pack(side=tk.LEFT, padx=5)
    
    def _direct_update(self):
        """Trigger a direct update download"""
        # Call the update service with auto_update=True and force show_message=True
        self.main_window.update_service.check_for_updates(show_message=True, auto_update=True)
    
    def _remove_direct_update_btn(self):
        """Remove the direct update button if it exists"""
        if hasattr(self, 'direct_update_btn'):
            self.direct_update_btn.destroy()
            delattr(self, 'direct_update_btn')
    
    def _get_display_api_url(self):
        """Convert internal API URL to display URL"""
        if self.api_service.api_url == "models":
            return "GGUF Models"
        return self.api_service.api_url
        
    def _get_internal_api_url(self, display_url):
        """Convert display URL to internal API URL"""
        if display_url == "GGUF Models":
            return "models"
        return display_url