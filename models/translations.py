import json
import os
import sys

TRANSLATIONS = {
    "English": {
        "settings": "Settings",
        "api_url": "API URL:",
        "model": "Model:",
        "server_status": "Server Status:",
        "server_status_checking": "Server Status: Checking...",
        "server_status_connected": "Server Status: Connected",
        "server_status_error": "Server Status: Error",
        "server_status_not_connected": "Server Status: Not Connected",
        "check_server": "Check Server",
        "setup_help": "Setup Help",
        "check_updates": "Check Updates",
        "new_version": "New Version Available",
        "up_to_date": "Up to Date",
        "input_words": "Input Words",
        "enter_words": "Enter words, separated by commas",
        "generate": "Generate",
        "append": "Append",
        "generating": "Generating sentences...",
        "generated_sentences": "Generated Sentences",
        "export_docx": "Export to Word",
        "show_all": "Show All",
        "hide_all": "Hide All",
        "delete_all": "Delete All",
        "show": "Show",
        "hide": "Hide",
        "copy": "Copy",
        "language": "Language:",
        "server_status_title": "Server Status",
        "server_connected_msg": "Successfully connected to Ollama server!\n\nServer version: {version}",
        "server_error_msg": "Unable to connect to Ollama server.\n\nPlease check if the server is running and the URL is correct.",
        "server_connection_error_msg": "Unable to connect to Ollama server. Please ensure:\n\n1. Ollama is installed\n2. Server is running ('ollama serve')\n3. API URL is correct\n\nError: {error}",
        "server_error_title": "Server Error",
        "server_connection_guide": "Unable to connect to Ollama server. Please ensure:\n1. Ollama is installed\n2. Server is running ('ollama serve')\n3. Model is installed ('ollama pull llama2')\nClick \"Setup Help\" for more information.",
        "warning_title": "Warning",
        "no_sentences_warning": "No sentences to export!",
        "document_title_prompt": "Enter document title:",
        "save_document_title": "Save Document",
        "export_success_title": "Success",
        "export_success_msg": "Document exported successfully!",
        "update_available_title": "Update Available",
        "update_available_msg": "New version available (v{version})!\n\nCurrent version: v{current_version}\n\nWould you like to visit the download page?",
        "no_updates_title": "No Updates",
        "no_updates_msg": "You are using the latest version (v{version})",
        "error_title": "Error",
        "update_check_error": "Failed to check for updates. Please try again later.",
        "update_error_msg": "Failed to check for updates:\n{error}",
        "prompt_error_msg": "Failed to read prompt file: {error}\nUsing default prompt.",
        "generation_error_msg": "Failed to generate sentence: {error}\nPlease check server settings and connection.",
        "unexpected_error_msg": "An unexpected error occurred: {error}",
        "startup_error_msg": "Error starting application:\n{error}",
        "using_default_prompt": "Using default prompt",
        "using_custom_prompt": "Using custom prompt",
        "toggle_prompt": "Toggle Prompt",
        "invalid_prompt_format": "Invalid prompt format: missing {word} placeholder.\nPlease add {word} placeholder in prompt.txt file."
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