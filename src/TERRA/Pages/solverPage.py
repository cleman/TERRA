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
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=10)

        solver_label = tk.Label(entry_frame, text="Solver Name:", font=("Arial", 14))
        solver_label.pack(pady=5, padx=5, side=tk.LEFT)
        solver_value = tk.StringVar(value="appsi_highs")
        #self.solver_entry = tk.Entry(entry_frame, width=20, font=("Arial", 14), textvariable=solver_value)
        #self.solver_entry.pack(pady=5, padx=5, side=tk.LEFT)
        self.solver_name_combobox = ttk.Combobox(entry_frame, values=["appsi_highs", "cbc_highs"], font=("Arial", 14), state="readonly")
        self.solver_name_combobox.current(0)
        self.solver_name_combobox.pack(pady=5, padx=5, side=tk.LEFT)

        # Spin box for time limit in seconds, default value is 600, min value is 1, max value is 3600, step is 10
        # Frame for spinbox
        spinbox_frame = tk.Frame(self)
        spinbox_frame.pack(pady=10)

        time_label = tk.Label(spinbox_frame, text="Time Limit (s):", font=("Arial", 14))
        time_label.pack(pady=5, padx=5, side=tk.LEFT)
        time_value = tk.StringVar(value="600")
        self.time_spinbox = tk.Spinbox(spinbox_frame, from_=1, to=3600, width=5, textvariable=time_value, font=("Arial", 14), increment=10)
        self.time_spinbox.pack(pady=5, padx=5, side=tk.LEFT)

        # Button to solve the problem
        solve_button = tk.Button(self, text="Solve", font=("Arial", 14), command=self.solve_problem)
        solve_button.pack(pady=20)

    def solve_problem(self):
        self.solver = Solver(self.tree)
        solver_name = self.solver_name_combobox.get()
        time_limit = int(self.time_spinbox.get())
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