import tkinter as tk
from tkinter import ttk

from tree import Tree

class otherPage(tk.Frame):
    def __init__(self, tree, parent, controller):
        tk.Frame.__init__(self, parent)

        self.tree = tree
        self.other_var = None
        self.refresh_callback = None
        self.raise_page_var = None

        # Titre principal centré en haut
        label = tk.Label(self, text="Other", font=("Arial", 24))
        label.pack(pady=20, padx=10)

        # 1. Un SEUL frame central qui va contenir la grille
        # On utilise .pack() pour le centrer globalement dans la fenêtre
        main_container = tk.Frame(self)
        main_container.pack(expand=True, fill=tk.Y)

        # Style pour aligner le texte à droite (optionnel, pour un look plus propre)
        label_options = {"anchor": "e"}

        # --- Ligne 0 : Nb step ---
        nb_step_label = tk.Label(main_container, text="Nb step", **label_options)
        nb_step_label.grid(row=0, column=0, padx=1, pady=5, sticky="e")
        
        self.nb_step_value = tk.IntVar(value=500)
        self.nb_step_spinbox = tk.Spinbox(main_container, from_=1, to=10000, textvariable=self.nb_step_value, width=8)
        self.nb_step_spinbox.grid(row=0, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 1 : Step length ---
        step_length_label = tk.Label(main_container, text="Step length:", **label_options)
        step_length_label.grid(row=1, column=0, padx=1, pady=5, sticky="e")
        
        self.step_length_value = tk.DoubleVar(value=10)
        self.step_length_spinbox = tk.Spinbox(main_container, from_=1, to=100, textvariable=self.step_length_value, width=8)
        self.step_length_spinbox.grid(row=1, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 2 : Min dist ---
        min_dist_label = tk.Label(main_container, text="Min dist:", **label_options)
        min_dist_label.grid(row=2, column=0, padx=1, pady=5, sticky="e")
        
        self.min_dist_value = tk.DoubleVar(value=10)
        self.min_dist_spinbox = tk.Spinbox(main_container, from_=1, to=100, textvariable=self.min_dist_value, width=8)
        self.min_dist_spinbox.grid(row=2, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 3 : Max dist ---
        max_dist_label = tk.Label(main_container, text="Max dist:", **label_options)
        max_dist_label.grid(row=3, column=0, padx=1, pady=5, sticky="e")
        
        self.max_dist_value = tk.DoubleVar(value=30)
        self.max_dist_spinbox = tk.Spinbox(main_container, from_=2, to=100, textvariable=self.max_dist_value, width=8)
        self.max_dist_spinbox.grid(row=3, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 4 : Max force ---
        max_force_label = tk.Label(main_container, text="Max force:", **label_options)
        max_force_label.grid(row=4, column=0, padx=1, pady=5, sticky="e")
        
        self.max_force_value = tk.DoubleVar(value=100)
        self.max_force_spinbox = tk.Spinbox(main_container, from_=1, to=10000, textvariable=self.max_force_value, width=8)
        self.max_force_spinbox.grid(row=4, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 5 : k coefficient ---
        k_label = tk.Label(main_container, text="k coefficient:", **label_options)
        k_label.grid(row=5, column=0, padx=1, pady=5, sticky="e")
        
        self.k_value = tk.DoubleVar(value=0.01)
        self.k_spinbox = tk.Spinbox(main_container, from_=0, to=1, textvariable=self.k_value, width=8)
        self.k_spinbox.grid(row=5, column=1, padx=1, pady=5, sticky="w")

        # Button to execute the local correction
        launch_button = tk.Button(self, text="Launch", font=("Arial", 14), command=self.local_correction)
        launch_button.pack(pady=20, side=tk.TOP)
    
    def local_correction(self):
        nbStep = int(self.nb_step_spinbox.get())
        stepLength = int(self.step_length_spinbox.get())
        minDist = float(self.min_dist_spinbox.get())
        maxDist = float(self.max_dist_spinbox.get())
        maxForce = float(self.max_force_spinbox.get())
        k = float(self.k_spinbox.get())

        print(f"Local correction, parameters : nbStep={nbStep}, stepLength={stepLength}, minDist={minDist}, maxDist={maxDist}, maxForce={maxForce}, k={k}")
        self.tree.local_correction(nbStep, stepLength, minDist, maxDist, maxForce, k)

        view_configuration = [True, True, False, False, True]

        # If the edges view is not enabled, enable it
        if self.other_var is not None:
            for i in range(len(view_configuration)):
                self.other_var[i].set(view_configuration[i])
        self.raise_page_var.set(4)

        # Refresh the map view to show the new edges
        if callable(self.refresh_callback):
            self.refresh_callback()