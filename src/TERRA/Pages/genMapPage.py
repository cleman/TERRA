import tkinter as tk
from tkinter import ttk


class generateMapPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Generate Map", font=("Arial", 24))
        label.pack(pady=10, padx=10)