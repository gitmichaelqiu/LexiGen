import tkinter as tk
from ui.main_window import MainWindow
from models.config import VERSION
from tkinter import messagebox
from models.translations import get_translation, load_translations
import traceback
import os
import sys

def find_libllama():
    import importlib.util

    # 1. Check if user has set LLAMA_CPP_LIB already
    if os.environ.get('LLAMA_CPP_LIB') and os.path.exists(os.environ['LLAMA_CPP_LIB']):
        return os.environ['LLAMA_CPP_LIB']
    # 2. Check common system locations
    system_paths = [
        '/usr/local/lib/libllama.dylib',
        '/usr/lib/libllama.dylib',
        '/opt/homebrew/lib/libllama.dylib',  # Apple Silicon Homebrew
    ]
    for path in system_paths:
        if os.path.exists(path):
            return path
    # 3. Check the llama_cpp package directory (for unpacked runs)
    spec = importlib.util.find_spec('llama_cpp')
    if spec and spec.submodule_search_locations:
        pkg_dir = spec.submodule_search_locations[0]
        candidate = os.path.join(pkg_dir, 'lib', 'libllama.dylib')
        if os.path.exists(candidate):
            return candidate
    # 4. If running as a bundled app, check bundled location
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        bundled_path = os.path.join(base_path, 'llama_cpp', 'lib', 'libllama.dylib')
        if os.path.exists(bundled_path):
            return bundled_path
    return None

libllama_path = find_libllama()
if libllama_path:
    os.environ['LLAMA_CPP_LIB'] = libllama_path

def main():
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        language = "English"
        load_translations()
        messagebox.showerror(
            get_translation(language, "error_title"), 
            get_translation(language, "startup_error_msg").format(error=str(e))
        )
        traceback.print_exc()

if __name__ == "__main__":
    main()