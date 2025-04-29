import os
import sys

# Version information
VERSION = "1.3.1"

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "http://127.0.0.1:11434/api/generate",
    "model": "qwen2.5:3b",
    "language": "English",
    "generate_prompt": "Create a simple sentence using the word '{word}'. The sentence should be clear and educational.",
    "analysis_prompt": "Analyze the grammatical usage of '{word}' in this sentence: '{sentence}'\nFocus on:\n1. Tense (e.g., Present Simple, Past Perfect)\n2. Voice (Active/Passive)\n3. Mood (Indicative/Subjunctive)\n4. Function (e.g., Subject, Object, Modifier)\n\nKeep the analysis concise and technical. Output in 1 line. Example format:\n\"Present Simple, Active Voice. Functions as the subject of the sentence.\" "
}

def get_assets_path():
    """
    Returns the path to the LexiGenAssets directory.
    This function handles both development mode and packaged applications.
    """
    if getattr(sys, 'frozen', False):
        # Running in a bundle (packaged)
        if sys.platform == 'darwin':
            # For macOS, get the parent directory of the .app bundle
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
        else:
            # For Windows, get the directory containing the .exe
            base_dir = os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment - assets are in parent directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir = os.path.dirname(base_dir)  # Go one level up from LexiGen directory
    
    assets_dir = os.path.join(base_dir, "LexiGenAssets")
    
    # Ensure the directory exists
    if not os.path.exists(assets_dir):
        try:
            os.makedirs(assets_dir)
        except Exception:
            pass
    
    return assets_dir

def get_translations_path():
    """Returns the path to the translations directory."""
    translations_dir = os.path.join(get_assets_path(), "translations")
    
    # Ensure the directory exists
    if not os.path.exists(translations_dir):
        try:
            os.makedirs(translations_dir)
        except Exception:
            pass
    
    return translations_dir

def get_settings_path():
    """Returns the path to the settings.yaml file."""
    return os.path.join(get_assets_path(), "settings.yaml")
