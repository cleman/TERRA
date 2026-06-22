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

        # region global elements
        # Main title, top centered
        label = tk.Label(self, text="Other", font=("Arial", 24))
        label.pack(pady=10, padx=10)

        # Frame for the local correction
        localCorrection_frame = tk.Frame(self, borderwidth=2, relief="groove")
        localCorrection_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        # Frame for the post processing method
        postProcessing_frame = tk.Frame(self, borderwidth=2, relief="groove")
        postProcessing_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)
        # endregion

        ################### Local Correction ###################
        # region Local Correction

        # After creating localCorrection_frame, configure columns to expand equally
        localCorrection_frame.columnconfigure(0, weight=1)
        localCorrection_frame.columnconfigure(1, weight=1)

        # Title for the local correction section, centered
        localCorrection_label = tk.Label(localCorrection_frame, text="Local correction", font=("Arial", 18))
        localCorrection_label.grid(row=0, column=0, columnspan=2, pady=10)

        # --- Ligne 0 : Nb step ---
        nb_step_label = tk.Label(localCorrection_frame, text="Nb step")
        nb_step_label.grid(row=1, column=0, padx=1, pady=5, sticky="e")
        
        self.nb_step_value = tk.IntVar(value=500)
        self.nb_step_spinbox = tk.Spinbox(localCorrection_frame, from_=1, to=10000, textvariable=self.nb_step_value, width=8)
        self.nb_step_spinbox.grid(row=1, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 1 : Step length ---
        step_length_label = tk.Label(localCorrection_frame, text="Step length:")
        step_length_label.grid(row=2, column=0, padx=1, pady=5, sticky="e")
        
        self.step_length_value = tk.DoubleVar(value=10)
        self.step_length_spinbox = tk.Spinbox(localCorrection_frame, from_=1, to=100, textvariable=self.step_length_value, width=8)
        self.step_length_spinbox.grid(row=2, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 2 : Min dist ---
        min_dist_label = tk.Label(localCorrection_frame, text="Min dist:")
        min_dist_label.grid(row=3, column=0, padx=1, pady=5, sticky="e")
        
        self.min_dist_value = tk.DoubleVar(value=10)
        self.min_dist_spinbox = tk.Spinbox(localCorrection_frame, from_=1, to=100, textvariable=self.min_dist_value, width=8)
        self.min_dist_spinbox.grid(row=3, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 3 : Max dist ---
        max_dist_label = tk.Label(localCorrection_frame, text="Max dist:")
        max_dist_label.grid(row=4, column=0, padx=1, pady=5, sticky="e")
        
        self.max_dist_value = tk.DoubleVar(value=30)
        self.max_dist_spinbox = tk.Spinbox(localCorrection_frame, from_=2, to=100, textvariable=self.max_dist_value, width=8)
        self.max_dist_spinbox.grid(row=4, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 4 : Max force ---
        max_force_label = tk.Label(localCorrection_frame, text="Max force:")
        max_force_label.grid(row=5, column=0, padx=1, pady=5, sticky="e")
        
        self.max_force_value = tk.DoubleVar(value=100)
        self.max_force_spinbox = tk.Spinbox(localCorrection_frame, from_=1, to=10000, textvariable=self.max_force_value, width=8)
        self.max_force_spinbox.grid(row=5, column=1, padx=1, pady=5, sticky="w")

        # --- Ligne 5 : k coefficient ---
        k_label = tk.Label(localCorrection_frame, text="k coefficient:")
        k_label.grid(row=6, column=0, padx=1, pady=5, sticky="e")
        
        self.k_value = tk.DoubleVar(value=0.01)
        self.k_spinbox = tk.Spinbox(localCorrection_frame, from_=0, to=1, textvariable=self.k_value, width=8)
        self.k_spinbox.grid(row=6, column=1, padx=1, pady=5, sticky="w")

        # Button to execute the local correction
        launch_button = tk.Button(localCorrection_frame, text="Launch", font=("Arial", 14), command=self.local_correction)
        launch_button.grid(row=7, column=0, columnspan=2, pady=20)
        
        # endregion
        

        ################### Post processing method ###################
        # region Post processing method

        postProcessing_frame.columnconfigure(0, weight=1)
        postProcessing_frame.columnconfigure(1, weight=1)

        # Title
        postProcessing_label = tk.Label(postProcessing_frame, text="Post processing", font=("Arial", 18))
        postProcessing_label.grid(row=0, column=0, columnspan=2, pady=10)

        # --- Ligne 0 : Angle Step ---
        angle_step_label = tk.Label(postProcessing_frame, text="Angle step:")
        angle_step_label.grid(row=1, column=0, padx=1, pady=5, sticky="e")

        self.angle_step_value = tk.DoubleVar(value=5)
        self.angle_step_spinbox = tk.Spinbox(postProcessing_frame, from_=1, to=360, textvariable=self.angle_step_value, width=8)
        self.angle_step_spinbox.grid(row=1, column=1, padx=1, pady=5, sticky="w")

        # Button to execute the post processing method
        post_processing_button = tk.Button(postProcessing_frame, text="Launch", font=("Arial", 14), command=self.post_processing)
        post_processing_button.grid(row=2, column=0, columnspan=2, pady=20)

        # endregion
    
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

    def post_processing(self):
        angleStep = float(self.angle_step_spinbox.get())
        print(f"Post processing, parameters : angleStep={angleStep}")
        self.tree.post_processing(angleStep)

        view_configuration = [True, True, False, False, True]

        # If the edges view is not enabled, enable it
        if self.other_var is not None:
            for i in range(len(view_configuration)):
                self.other_var[i].set(view_configuration[i])
        self.raise_page_var.set(4)

        # Refresh the map view to show the new edges
        if callable(self.refresh_callback):
            self.refresh_callback()