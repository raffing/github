import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from gui import create_gui
from excel_utils import load_excel_data
from filters import apply_filters
from categories import manage_categories

class ExcelSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Search Application")
        self.data = None
        self.filtered_data = None
        
        self.create_menu()
        self.create_gui()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Excel File", command=self.load_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            try:
                self.data = load_excel_data(file_path)
                self.filtered_data = self.data
                messagebox.showinfo("Success", "Excel file loaded successfully!")
                self.update_gui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel file: {e}")

    def update_gui(self):
        # Placeholder for GUI update logic
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSearchApp(root)
    root.mainloop()