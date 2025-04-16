import os
import json
from models.config import DEFAULT_CONFIG

class SettingsService:
    """Service for managing application settings and persistence."""
    
    # Define settings that should not be persisted
    EXCLUDED_SETTINGS = ['prompt_file', 'default_prompt']
    
    def __init__(self, config_path="settings.json"):
        """Initialize settings service with specified config path."""
        self.config_path = config_path
        self.settings = {}
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file or use defaults if file doesn't exist."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    
                # Ensure all required settings exist by filling gaps with defaults
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self.settings and key not in self.EXCLUDED_SETTINGS:
                        self.settings[key] = value
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
                self._initialize_default_settings()
        else:
            # Use default settings if file doesn't exist
            self._initialize_default_settings()
    
    def _initialize_default_settings(self):
        """Initialize settings with default values, excluding those that shouldn't be persisted."""
        self.settings = {k: v for k, v in DEFAULT_CONFIG.items() if k not in self.EXCLUDED_SETTINGS}
    
    def save_settings(self):
        """Save current settings to JSON file, excluding certain parameters."""
        try:
            # Make a copy of settings and filter out excluded settings
            settings_to_save = {k: v for k, v in self.settings.items() if k not in self.EXCLUDED_SETTINGS}
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a setting value by key with optional default."""
        # For excluded settings, always return from DEFAULT_CONFIG
        if key in self.EXCLUDED_SETTINGS:
            return DEFAULT_CONFIG.get(key, default)
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value by key and save settings."""
        # Don't save excluded settings to the settings dictionary
        if key not in self.EXCLUDED_SETTINGS:
            self.settings[key] = value
            return self.save_settings()
        return False
    
    def update_settings(self, settings_dict):
        """Update multiple settings at once and save settings."""
        # Filter out excluded settings before updating
        filtered_settings = {k: v for k, v in settings_dict.items() if k not in self.EXCLUDED_SETTINGS}
        self.settings.update(filtered_settings)
        return self.save_settings() 