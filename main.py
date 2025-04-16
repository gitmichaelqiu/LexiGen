import tkinter as tk
from ui.main_window import MainWindow
from models.config import VERSION
from tkinter import messagebox
import traceback

def main():
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error starting application:\n{str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()