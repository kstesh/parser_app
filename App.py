import re
import tkinter as tk
from tkinter import filedialog
from Processor import Processor



class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Search Application")
        self.geometry("400x200")
        self.resizable(False, False)

        # Term input
        self.term_label = tk.Label(self, text="Enter Term:")
        self.term_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        self.term_entry = tk.Entry(self)
        self.term_entry.grid(row=0, column=1, padx=5, pady=5)

        # Folder path input
        self.path_label = tk.Label(self, text="Enter Folder Path:")
        self.path_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

        self.path_entry = tk.Entry(self)
        self.path_entry.grid(row=1, column=1, padx=5, pady=5)

        self.path_entry.insert(0, Processor.get_last_path())

        self.browse_button = tk.Button(self, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        # Search button
        self.search_button = tk.Button(self, text="Search", command=self.search_data)
        self.search_button.grid(row=2, column=1, pady=10)

        # Result label
        self.result_label = tk.Label(self, text="")
        self.result_label.grid(row=3, column=0, columnspan=3, pady=10)

        self.bind_all("<Key>", self._onKeyRelease, "+")

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_path)

    def search_data(self):
        self.result_label.config(text="Почалась обробка!")
        term = self.term_entry.get()
        path = self.path_entry.get()

        is_empty = lambda s: len(s) == 0 or s.isspace() or not re.search(r'[a-zA-Z0-9\u0400-\u04FF]', s)
        if is_empty(term) or is_empty(path):
            self.result_label.config(text="Запит або шлях некоректний")
        else:
            processor = Processor()
            processor.search_data(term, path)
            self.result_label.config(text="Обробку закінчено!")

    def handle_key_release(self, event, entry):
        # Обробник події відпускання клавіші
        if event.state == 4 and event.keysym.lower() == 'v':  # 4 відповідає за клавішу Control
            self.handle_paste(entry)

    def handle_paste(self, entry):
        # Обробник події вставки (Ctrl+V)
        text = self.clipboard_get()
        if entry:
            entry.insert(tk.INSERT, text)

    @staticmethod
    def _onKeyRelease(event):
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
            event.widget.event_generate("<<SelectAll>>")
