import os
import json
import yaml
from models.config import DEFAULT_CONFIG, get_settings_path

class SettingsService:
    """Service for managing application settings and persistence."""
    
    def __init__(self, config_path=None):
        """Initialize settings service with specified config path."""
        self.config_path = config_path if config_path else get_settings_path()
        self.settings = {}
        self.external_generation_prompt = None
        self.external_analysis_prompt = None
        self.external_tense_prompt = None
        self.external_analysis_tense_prompt = None
        self.external_context_attachment_prompt = None
        self.load_settings()

    
    def load_settings(self):
        """Load settings from YAML file or use defaults if file doesn't exist."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.settings = yaml.safe_load(f) or {}
                # Ensure all required settings exist by filling gaps with defaults
                for key, value in DEFAULT_CONFIG.items():
                    if key == 'generation_prompt':
                        self.external_generation_prompt = self.settings.get('generation_prompt')
                    elif key == 'analysis_prompt':
                        self.external_analysis_prompt = self.settings.get('analysis_prompt')
                    elif key == 'tense_prompt':
                        self.external_tense_prompt = self.settings.get('tense_prompt')
                    elif key == 'analysis_tense_prompt':
                        self.external_analysis_tense_prompt = self.settings.get('analysis_tense_prompt')
                    elif key == 'context_attachment_prompt':
                        self.external_context_attachment_prompt = self.settings.get('context_attachment_prompt')
                    if key not in self.settings or key in ['generation_prompt', 'analysis_prompt', 'tense_prompt', 'analysis_tense_prompt', 'context_attachment_prompt']:
                        self.settings[key] = value
            except Exception as e:
                self._initialize_default_settings()
        else:
            # Use default settings if file doesn't exist
            self._initialize_default_settings()
    
    def _initialize_default_settings(self):
        """Initialize settings with default values, excluding those that shouldn't be persisted."""
        self.settings = {k: v for k, v in DEFAULT_CONFIG.items()}
    
    def save_settings(self):
        """Save current settings to YAML file, excluding certain parameters."""

        # Save the external prompts to the settings file
        self.settings['generation_prompt'] = self.external_generation_prompt
        self.settings['analysis_prompt'] = self.external_analysis_prompt
        self.settings['tense_prompt'] = self.external_tense_prompt
        self.settings['analysis_tense_prompt'] = self.external_analysis_tense_prompt
        self.settings['context_attachment_prompt'] = self.external_context_attachment_prompt
        try:
            # Make a copy of settings and filter out excluded settings
            settings_to_save = {k: v for k, v in self.settings.items()}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(settings_to_save, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            return False
    
    def get_setting(self, key, default=None):
        """Get a setting value by key with optional default."""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value by key and save settings."""
        self.settings[key] = value
        return self.save_settings()
    
    def update_settings(self, settings_dict):
        """Update multiple settings at once and save settings."""
        # Filter out excluded settings before updating
        filtered_settings = {k: v for k, v in settings_dict.items()}
        self.settings.update(filtered_settings)
        return self.save_settings() 
    
    def get_settings(self, key):
        """Get a setting value by key (no default, for strict access)."""
        return self.settings.get(key) 