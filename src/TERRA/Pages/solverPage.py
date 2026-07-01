import tkinter as tk
from tkinter import ttk

from tree import Tree
from solver import Solver

class SolverPage(tk.Frame):
    def __init__(self, tree, parent, controller):
        tk.Frame.__init__(self, parent)

        self.tree = tree
        self.solver = None
        self.solver_var = None
        self.refresh_callback = None
        self.raise_page_var = None

        label = tk.Label(self, text="Solver", font=("Arial", 24))
        label.pack(pady=10, padx=10)

        # Text entry for solver name, default value is "appsi_highs"
        # Frame for entry
        solver_parameters_frame = tk.Frame(self)
        solver_parameters_frame.pack(pady=10)

        ################### Solver parameters ###################
        # region Local Correction

        # After creating localCorrection_frame, configure columns to expand equally
        solver_parameters_frame.columnconfigure(0, weight=1)
        solver_parameters_frame.columnconfigure(1, weight=1)

        # Name of the solver to use
        solver_label = tk.Label(solver_parameters_frame, text="Solver Name:", font=("Arial", 14))
        solver_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        #solver_value = tk.StringVar(value="appsi_highs")

        self.solver_name_combobox = ttk.Combobox(solver_parameters_frame, values=["appsi_highs", "cbc_highs"], font=("Arial", 14), state="readonly")
        self.solver_name_combobox.current(0)
        self.solver_name_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Version of the solver to use
        solver_version_label = tk.Label(solver_parameters_frame, text="Solver Version:", font=("Arial", 14))
        solver_version_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.solver_version_combobox = ttk.Combobox(solver_parameters_frame, values=["1.0"], font=("Arial", 14), state="readonly")
        self.solver_version_combobox.current(0)
        self.solver_version_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Cost function to use
        cost_function_label = tk.Label(solver_parameters_frame, text="Cost Function:", font=("Arial", 14))
        cost_function_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cost_function_combobox = ttk.Combobox(solver_parameters_frame, values=["approximate", "linear", "network model"], font=("Arial", 14), state="readonly")
        self.cost_function_combobox.current(0)
        self.cost_function_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Maximum number of relays allowed, default value is 10
        max_relays_label = tk.Label(solver_parameters_frame, text="Max Relays:", font=("Arial", 14))
        max_relays_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.max_relays_value = tk.IntVar(value=10)
        self.max_relays_spinbox = tk.Spinbox(solver_parameters_frame, from_=1, to=100, width=5, textvariable=self.max_relays_value, font=("Arial", 14))
        self.max_relays_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        time_label = tk.Label(solver_parameters_frame, text="Time Limit (s):", font=("Arial", 14))
        time_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        time_value = tk.StringVar(value="600")
        self.time_spinbox = tk.Spinbox(solver_parameters_frame, from_=1, to=3600, width=5, textvariable=time_value, font=("Arial", 14), increment=10)
        self.time_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Button to solve the problem
        solve_button = tk.Button(self, text="Solve", font=("Arial", 14), command=self.solve_problem)
        solve_button.pack(pady=20)

    def solve_problem(self):

        # Get solver parameters from the GUI
        solver_name = self.solver_name_combobox.get()
        solver_version = self.solver_version_combobox.get()
        cost_function = self.cost_function_combobox.get()
        max_relays = int(self.max_relays_spinbox.get())
        time_limit = int(self.time_spinbox.get())
        
        self.solver = Solver(self.tree, max_relays)

        print(f"Solving problem with solver {solver_name} and time limit {time_limit} seconds")
        self.solver.solve(solver_name, time_limit)
        print(f"Solution: {self.solver.get_solution()}")

        view_configuration = [True, True, False, False, True]

        # If the edges view is not enabled, enable it
        if self.solver_var is not None:
            for i in range(len(view_configuration)):
                self.solver_var[i].set(view_configuration[i])
        self.raise_page_var.set(4)

        # Refresh the map view to show the new edges
        if callable(self.refresh_callback):
            self.refresh_callback()