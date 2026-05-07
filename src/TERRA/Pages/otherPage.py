import tkinter as tk
from tkinter import ttk


class otherPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Other", font=("Arial", 24))
        label.pack(pady=10, padx=10)