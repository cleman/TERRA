import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

from tree import Tree

class generateGridPage(tk.Frame):
    def __init__(self, tree, parent, controller):
        tk.Frame.__init__(self, parent)

        self.tree = tree
        self.candidates_var = None
        self.refresh_callback = None
        self.raise_page_var = None

        label = tk.Label(self, text="Generate Grid", font=("Arial", 24))
        label.pack(pady=10, padx=10)

        # Frame for spinbox
        spinbox_frame = tk.Frame(self)
        spinbox_frame.pack(pady=10)

        # Spin box for grid size.default value is 20, min value is 1, max value is 100
        size_label = tk.Label(spinbox_frame, text="Grid Size:", font=("Arial", 14))
        size_label.pack(pady=5, padx=5, side=tk.LEFT)
        size_value = StringVar(value="20")
        self.size_spinbox = tk.Spinbox(spinbox_frame, from_=1, to=100, width=5, textvariable=size_value, font=("Arial", 14))
        self.size_spinbox.pack(pady=5, padx=5, side=tk.LEFT)

        # Checkbox to include obstacles points, default value is True
        self.obstacles_var = tk.BooleanVar(value=True)
        obstacles_checkbox = tk.Checkbutton(self, text="Include Obstacles", variable=self.obstacles_var, font=("Arial", 14))
        obstacles_checkbox.pack(pady=5)

        # Button to generate the grid
        generate_button = tk.Button(self, text="Generate Grid", font=("Arial", 14), command=self.generate_grid)
        generate_button.pack(pady=20)


    def generate_grid(self):
        size = int(float(self.size_spinbox.get()))
        include_obstacles = self.obstacles_var.get()
        print(f"Generating grid of size {size} with obstacles: {include_obstacles}")

        view_configuration = [True, True, True, False, False]

        if self.candidates_var is not None:
            for i in range (len(view_configuration)):
                self.candidates_var[i].set(view_configuration[i])
        self.raise_page_var.set(2)

        self.tree.generate_discrete_grid(size, include_obstacles)

        if callable(self.refresh_callback):
            self.refresh_callback()