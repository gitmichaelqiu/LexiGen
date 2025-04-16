import os
import json
from models.config import DEFAULT_CONFIG

class SettingsService:
    """Service for managing application settings and persistence."""
    
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
                    if key not in self.settings:
                        self.settings[key] = value
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
                self.settings = DEFAULT_CONFIG.copy()
        else:
            # Use default settings if file doesn't exist
            self.settings = DEFAULT_CONFIG.copy()
    
    def save_settings(self):
        """Save current settings to JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
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
        self.settings.update(settings_dict)
        return self.save_settings() 