import tkinter as tk
from tkinter import ttk

from tree import Tree

class generateEdgesPage(tk.Frame):
    def __init__(self, tree, parent, controller):
        tk.Frame.__init__(self, parent)

        self.tree = tree
        self.candidates_edges_var = None
        self.refresh_callback = None
        self.raise_page_var = None

        label = tk.Label(self, text="Generate Edges", font=("Arial", 24))
        label.pack(pady=10, padx=10)

        # Maximum distance between two points to be connected by an edge. Default value is 30, min value is 1, max value is 100
        # Frame for spinbox
        spinbox_frame = tk.Frame(self)
        spinbox_frame.pack(pady=10)

        distance_label = tk.Label(spinbox_frame, text="Max Distance:", font=("Arial", 14))
        distance_label.pack(pady=5, padx=5, side=tk.LEFT)
        distance_value = tk.StringVar(value="30")
        self.distance_spinbox = tk.Spinbox(spinbox_frame, from_=1, to=100, width=5, textvariable=distance_value, font=("Arial", 14))
        self.distance_spinbox.pack(pady=5, padx=5, side=tk.LEFT)

        # Button to generate the edges
        generate_button = tk.Button(self, text="Generate Edges", font=("Arial", 14), command=self.generate_edges)
        generate_button.pack(pady=20)


    def generate_edges(self):
        distance = int(self.distance_spinbox.get())
        print(f"Generating edges with distance {distance}")
        self.tree.compute_edges(distance)
        print(f"Number of edges: {len(self.tree.get_edges())}")

        view_configuration = [True, True, True, True, False]

        # If the edges view is not enabled, enable it
        if self.candidates_edges_var is not None:
            for i in range (len(view_configuration)):
                self.candidates_edges_var[i].set(view_configuration[i])
        self.raise_page_var.set(3)

        # Refresh the map view to show the new edges
        if callable(self.refresh_callback):
            self.refresh_callback()
        

