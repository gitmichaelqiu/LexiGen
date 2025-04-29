import tkinter as tk
from ui.main_window import MainWindow
from models.config import VERSION
from tkinter import messagebox
from models.translations import get_translation, load_translations
import traceback

def main():
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        # Load default English translation since we're not initialized yet
        language = "English"
        load_translations()
        messagebox.showerror(
            get_translation(language, "error_title"), 
            get_translation(language, "startup_error_msg").format(error=str(e))
        )
        traceback.print_exc()

if __name__ == "__main__":
    main()