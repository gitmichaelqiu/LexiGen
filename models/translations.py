import json
import os
import sys

TRANSLATIONS = {
    "English": {
        "settings": "Settings",
        "api_url": "API URL:",
        "model": "Model:",
        # ... (保持所有原始翻译不变)
    }
}

def load_translations():
    """Load translations from external files."""
    try:
        # Get the application's base directory
        if getattr(sys, 'frozen', False):
            if sys.platform == 'darwin':
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
            else:
                base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        translations_dir = os.path.join(base_dir, "translations")
        
        if not os.path.exists(translations_dir):
            try:
                os.makedirs(translations_dir)
            except Exception:
                pass
        
        if os.path.exists(translations_dir):
            try:
                files = os.listdir(translations_dir)
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(translations_dir, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lang_translations = json.load(f)
                                TRANSLATIONS.update(lang_translations)
                        except Exception:
                            continue
            except Exception:
                pass
        
        return list(TRANSLATIONS.keys())
    except Exception:
        return list(TRANSLATIONS.keys())

def get_translation(language, key):
    """Get translation for the given language and key."""
    return TRANSLATIONS.get(language, {}).get(key, key)