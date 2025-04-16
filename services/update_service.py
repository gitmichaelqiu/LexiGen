import requests
import webbrowser
from tkinter import messagebox
from models.config import VERSION
from models.translations import get_translation

class UpdateService:
    def __init__(self, language="English"):
        self.language = language

    def check_for_updates(self, show_message=True):
        try:
            response = requests.get("https://api.github.com/repos/gitmichaelqiu/LexiGen/releases/latest")
            if response.status_code == 200:
                latest_version = response.json()["tag_name"].lstrip('v')
                if latest_version > VERSION:
                    if show_message and messagebox.askyesno(
                        get_translation(self.language, "update_available_title"),
                        get_translation(self.language, "update_available_msg").format(
                            version=latest_version,
                            current_version=VERSION
                        )
                    ):
                        webbrowser.open("https://github.com/gitmichaelqiu/LexiGen/releases/latest")
                    return "new_version"
                else:
                    if show_message:
                        messagebox.showinfo(
                            get_translation(self.language, "no_updates_title"),
                            get_translation(self.language, "no_updates_msg").format(version=VERSION)
                        )
                    return "up_to_date"
            else:
                if show_message:
                    messagebox.showerror(
                        "Error",
                        get_translation(self.language, "update_check_error")
                    )
                return "error"
        except Exception as e:
            if show_message:
                messagebox.showerror(
                    "Error",
                    get_translation(self.language, "update_error_msg").format(error=str(e))
                )
            return "error"