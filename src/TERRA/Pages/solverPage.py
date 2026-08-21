import tkinter as tk
from tkinter import ttk

from tree import Tree
from solver import Solver
from solver_2 import Solver as Solver2

class SolverPage(tk.Frame):
    def __init__(self, tree, parent, controller):
        tk.Frame.__init__(self, parent)

        self.tree = tree
        self.solver = None
        self.solver_var = None
        self.refresh_callback = None
        self.raise_page_var = None

        #label = tk.Label(self, text="Solver", font=("Arial", 24))
        #label.pack(pady=10, padx=10)

        # Frame for the first solver
        solver_parameters_frame = tk.Frame(self, borderwidth=2, relief="groove")
        solver_parameters_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        # Frame for the second solver
        solver_2_parameters_frame = tk.Frame(self, borderwidth=2, relief="groove")
        solver_2_parameters_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        ################### Solver parameters ###################
        # region solver 1

        # After creating solver_parameters_frame, configure columns to expand equally
        solver_parameters_frame.columnconfigure(0, weight=1)
        solver_parameters_frame.columnconfigure(1, weight=1)

        # Title for the solver section, centered
        solver_title_label = tk.Label(solver_parameters_frame, text="Solver 1 Parameters", font=("Arial", 18))
        solver_title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Name of the solver to use
        solver_label = tk.Label(solver_parameters_frame, text="Solver Name:", font=("Arial", 14))
        solver_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        #solver_value = tk.StringVar(value="appsi_highs")

        self.solver_name_combobox = ttk.Combobox(solver_parameters_frame, values=["appsi_highs", "cbc"], font=("Arial", 14), state="readonly")
        self.solver_name_combobox.current(0)
        self.solver_name_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Version of the solver to use
        solver_version_label = tk.Label(solver_parameters_frame, text="Solver Version:", font=("Arial", 14))
        solver_version_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.solver_version_combobox = ttk.Combobox(solver_parameters_frame, values=["1.0"], font=("Arial", 14), state="readonly")
        self.solver_version_combobox.current(0)
        self.solver_version_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Cost function to use
        cost_function_label = tk.Label(solver_parameters_frame, text="Cost Function:", font=("Arial", 14))
        cost_function_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.cost_function_combobox = ttk.Combobox(solver_parameters_frame, values=["approximate", "linear", "network model"], font=("Arial", 14), state="readonly")
        self.cost_function_combobox.current(0)
        self.cost_function_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Maximum number of relays allowed, default value is 10
        max_relays_label = tk.Label(solver_parameters_frame, text="Max Relays:", font=("Arial", 14))
        max_relays_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.max_relays_value = tk.IntVar(value=10)
        self.max_relays_spinbox = tk.Spinbox(solver_parameters_frame, from_=0, to=100, width=5, textvariable=self.max_relays_value, font=("Arial", 14))
        self.max_relays_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        time_label = tk.Label(solver_parameters_frame, text="Time Limit (s):", font=("Arial", 14))
        time_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        time_value = tk.StringVar(value="600")
        self.time_spinbox = tk.Spinbox(solver_parameters_frame, from_=1, to=3600, width=5, textvariable=time_value, font=("Arial", 14), increment=10)
        self.time_spinbox.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Button to solve the problem
        solve_button = tk.Button(solver_parameters_frame, text="Solve", font=("Arial", 14), command=self.solve_problem)
        solve_button.grid(row=6, column=0, columnspan=2, pady=10)


        ################### Solver 2 (Network-based) parameters ###################
        # region solver 2

        # After creating solver_parameters_frame, configure columns to expand equally
        solver_2_parameters_frame.columnconfigure(0, weight=1)
        solver_2_parameters_frame.columnconfigure(1, weight=1)

        row_ = 0

        # region Title for the solver section, centered
        solver_2_title_label = tk.Label(solver_2_parameters_frame, text="Solver 2 Parameters", font=("Arial", 18))
        solver_2_title_label.grid(row=row_, column=0, columnspan=2, pady=10)
        row_ += 1
        # endregion

        # region Maximum number of relays allowed, default value is 10
        solver_2_max_relays_label = tk.Label(solver_2_parameters_frame, text="Max Relays:", font=("Arial", 14))
        solver_2_max_relays_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        self.solver_2_max_relays_value = tk.IntVar(value=10)
        self.solver_2_max_relays_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=0, to=100, width=5, textvariable=self.solver_2_max_relays_value, font=("Arial", 14))
        self.solver_2_max_relays_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region Unit capacity of the links, default value is 5e6 (5 Mbps) : C_0
        solver_2_unit_capacity_label = tk.Label(solver_2_parameters_frame, text="Unit Capacity (Mbps):", font=("Arial", 14))
        solver_2_unit_capacity_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        self.solver_2_unit_capacity_value = tk.DoubleVar(value=5)
        self.solver_2_unit_capacity_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=1, to=1100, width=5, textvariable=self.solver_2_unit_capacity_value, font=("Arial", 14), increment=1)
        self.solver_2_unit_capacity_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region Maximum packet loss rate per link, default value is 2% : PLR_max
        solver_2_plr_max_label = tk.Label(solver_2_parameters_frame, text="Max PLR (%):", font=("Arial", 14))
        solver_2_plr_max_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        self.solver_2_plr_max_value = tk.DoubleVar(value=2)
        self.solver_2_plr_max_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=0, to=100, width=5, textvariable=self.solver_2_plr_max_value, font=("Arial", 14), increment=0.1)
        self.solver_2_plr_max_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region path loss exponent, default value is 3.0 : n
        solver_2_path_loss_exponent_label = tk.Label(solver_2_parameters_frame, text="Path Loss Exponent:", font=("Arial", 14))
        solver_2_path_loss_exponent_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        self.solver_2_path_loss_exponent_value = tk.DoubleVar(value=3.0)
        self.solver_2_path_loss_exponent_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=1.0, to=10.0, width=5, textvariable=self.solver_2_path_loss_exponent_value, font=("Arial", 14), increment=0.1)
        self.solver_2_path_loss_exponent_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region packet size in bytes, default value is 1000 bytes : l
        solver_2_packet_size_label = tk.Label(solver_2_parameters_frame, text="Packet Size (bytes):", font=("Arial", 14))
        solver_2_packet_size_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        self.solver_2_packet_size_value = tk.IntVar(value=1000)
        self.solver_2_packet_size_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=1, to=10000, width=5, textvariable=self.solver_2_packet_size_value, font=("Arial", 14), increment=10)
        self.solver_2_packet_size_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region Time limit for the solver, default value is 600 seconds
        solver_2_time_label = tk.Label(solver_2_parameters_frame, text="Time Limit (s):", font=("Arial", 14))
        solver_2_time_label.grid(row=row_, column=0, padx=5, pady=5, sticky="e")
        solver_2_time_value = tk.StringVar(value="600")
        self.solver_2_time_spinbox = tk.Spinbox(solver_2_parameters_frame, from_=1, to=3600, width=5, textvariable=solver_2_time_value, font=("Arial", 14), increment=10)
        self.solver_2_time_spinbox.grid(row=row_, column=1, padx=5, pady=5, sticky="w")
        row_ += 1
        # endregion

        # region objective function weights, default values are alpha=0.8, beta=0.1, gamma=0.1, side by side in a grid layout

        # Draw a line
        solver_2_weights_line = ttk.Separator(solver_2_parameters_frame, orient='horizontal')
        solver_2_weights_line.grid(row=row_, column=0, columnspan=2, sticky="ew", padx=40, pady=5)
        row_ += 1

        solver_2_weights_grid_frame = tk.Frame(solver_2_parameters_frame)
        solver_2_weights_grid_frame.grid(row=row_, column=0, columnspan=2, padx=5, pady=5)
        solver_2_weights_grid_frame.columnconfigure(0, weight=1)
        solver_2_weights_grid_frame.columnconfigure(1, weight=1)
        solver_2_weights_grid_frame.columnconfigure(2, weight=1)

        alpha_label = tk.Label(solver_2_weights_grid_frame, text="Alpha", font=("Arial", 14))       # Alpha: Delay
        alpha_label.grid(row=0, column=0, padx=5, pady=5)
        beta_label = tk.Label(solver_2_weights_grid_frame, text="Beta", font=("Arial", 14))         # Beta: Packet Loss Rate
        beta_label.grid(row=0, column=1, padx=5, pady=5)
        gamma_label = tk.Label(solver_2_weights_grid_frame, text="Gamma", font=("Arial", 14))       # Gamma: Number of Relays
        gamma_label.grid(row=0, column=2, padx=5, pady=5)

        # Alpha
        self.solver_2_alpha_value = tk.DoubleVar(value=0.8)
        self.solver_2_alpha_spinbox = tk.Spinbox(solver_2_weights_grid_frame, from_=0.0, to=10.0, width=5, textvariable=self.solver_2_alpha_value, font=("Arial", 14), increment=0.01)
        self.solver_2_alpha_spinbox.grid(row=1, column=0, padx=5, pady=5)
        
        # Beta
        self.solver_2_beta_value = tk.DoubleVar(value=0.1)
        self.solver_2_beta_spinbox = tk.Spinbox(solver_2_weights_grid_frame, from_=0.0, to=10.0, width=5, textvariable=self.solver_2_beta_value, font=("Arial", 14), increment=0.01)
        self.solver_2_beta_spinbox.grid(row=1, column=1, padx=5, pady=5)

        # Gamma
        self.solver_2_gamma_value = tk.DoubleVar(value=0.01)
        self.solver_2_gamma_spinbox = tk.Spinbox(solver_2_weights_grid_frame, from_=0.0, to=10.0, width=5, textvariable=self.solver_2_gamma_value, font=("Arial", 14), increment=0.01)
        self.solver_2_gamma_spinbox.grid(row=1, column=2, padx=5, pady=5)
        row_ += 1

        # Draw a line
        solver_2_weights_line_2 = ttk.Separator(solver_2_parameters_frame, orient='horizontal')
        solver_2_weights_line_2.grid(row=row_, column=0, columnspan=2, sticky="ew", padx=40, pady=5)
        row_ += 1
        # endregion

        # region Button to solve the problem
        solver_2_solve_button = tk.Button(solver_2_parameters_frame, text="Solve", font=("Arial", 14), command=self.solve_2_problem)
        solver_2_solve_button.grid(row=row_, column=0, columnspan=2, pady=10)
        # endregion

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
    
    def solve_2_problem(self):

        # Get solver parameters from the GUI
        max_relays = int(self.solver_2_max_relays_spinbox.get())
        unit_capacity = float(self.solver_2_unit_capacity_spinbox.get())
        plr_max = float(self.solver_2_plr_max_spinbox.get())
        path_loss_exponent = float(self.solver_2_path_loss_exponent_spinbox.get())
        packet_size = int(self.solver_2_packet_size_spinbox.get())
        time_limit = int(self.solver_2_time_spinbox.get())
        alpha = float(self.solver_2_alpha_spinbox.get())
        beta = float(self.solver_2_beta_spinbox.get())
        gamma = float(self.solver_2_gamma_spinbox.get())

        # Update the physical parameters of the tree
        self.tree.physical_parameters["C_min"] = unit_capacity * 1e6
        self.tree.physical_parameters["n_PLE"] = path_loss_exponent
        self.tree.physical_parameters["l"] = packet_size * 8  # Convert bytes

        solver_parameters = {
            "max_relays": max_relays,
            "unit_capacity": unit_capacity,
            "plr_max": plr_max,
            "path_loss_exponent": path_loss_exponent,
            "packet_size": packet_size,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma
        }
        unserved_terminals = []

        passed = False
        while not passed:
            self.solver = Solver2(self.tree, solver_parameters, unserved_terminals)

            print(f"Solving problem with time limit {time_limit} seconds")
            passed = self.solver.solve(time_limit)
            print(f"Solver returned: {passed}")


            if not passed:
                # Remove the further terminal from the tree and try again
                terminal_to_remove, _ = self.tree.get_terminal_to_remove(unserved_terminals)
                if terminal_to_remove is not None:
                    print(f"Removing furthest terminal {terminal_to_remove} and trying again.")
                    unserved_terminals += [terminal_to_remove]
                else:
                    print("No more terminals to remove. Cannot find a feasible solution.")
                    break

        # Update unserved terminals in the tree
        self.tree.set_unserved_terminals(unserved_terminals)

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