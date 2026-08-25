from utils import fcost, compute_distance, C_PLR_D
from tree import Tree
import pyomo.environ as pyo
import time
import sys
import numpy as np

import math

# region Parameters
############## Parameters to move to a config file ##############
# Objective function weights
alpha = 0.8
beta = 1.0 - alpha
gamma = 0.2

# QOS
C_min = 5e6       # Mbps, minimum capacity per link
C0 = 5e6          # Mbps, reference throughput for congestion calculation
PLR_max = 0.05  # maximum packet loss rate per link
rho_max = 0.8   # maximum congestion per link
D0 = 0.05
# endregion

class Solver:
    def __init__(self, tree, params, terminals_to_remove=[]):
        self.tree = tree

        self.max_relays = params.get("max_relays", 10)
        self.unit_throughput = params.get("unit_throughput", C0)*1e6
        self.plr_max = params.get("plr_max", PLR_max * 100) / 100
        self.path_loss_exponent = params.get("path_loss_exponent", 3.5)
        self.packet_size = params.get("packet_size", 8 * 1000)
        self.alpha = params.get("alpha", alpha)
        self.beta = params.get("beta", beta)
        self.gamma = params.get("gamma", gamma)

        tree.weights = [self.alpha, self.beta, self.gamma]
        tree.ref_values = [D0, self.plr_max, self.max_relays]

        self.terminals_to_remove = terminals_to_remove

        self.model = None
        self.solver = None
        self.solution = None
        self.score_matrix = None

        tree.solver_used = 2  # Mark that this solver is used for the current solution

        self.build_score_matrix()

        self.build_model()
    
    # Build the cost matrix for the given tree
    def build_score_matrix(self):
        # Initialize the cost matrix with a large value (infinity) for non-existing edges and 0 for diagonal elements
        score_matrix = np.full((3, len(self.tree.points), len(self.tree.points)), 1e12, dtype=float)
        score_matrix[0] = np.zeros((len(self.tree.points), len(self.tree.points)), dtype=float)  # Initialize the first layer with zeros
        score_matrix[1] = 0.8 * np.ones((len(self.tree.points), len(self.tree.points)), dtype=float)  # Initialize the second layer with 0.8

        # Computte the score matrix based on the edges in the tree
        for e in self.tree.edges:
            if e[2] > 1e10:
                continue

            capacity, plr, delay = C_PLR_D(e[2], self.unit_throughput, self.path_loss_exponent, self.packet_size)

            if capacity > 0 and plr >= 1.0:
                plr =  0.8

            score_matrix[0, e[0], e[1]] = capacity
            score_matrix[0, e[1], e[0]] = capacity
            score_matrix[1, e[0], e[1]] = plr
            score_matrix[1, e[1], e[0]] = plr
            score_matrix[2, e[0], e[1]] = delay
            score_matrix[2, e[1], e[0]] = delay

        self.score_matrix = score_matrix

    # Build the optimization model for the given tree
    def build_model(self):
        # region PLR linearization
        plr_points = [math.log(1+i/100) for i in range(-5, 1, 1)]
        plr_values = [(1 - math.exp(p))**2 for p in plr_points]
        # endregion

        points = self.tree.points
        nb_terminals = self.tree.get_nb_terminals()

        # region Nodes indices
        N_indices = [i for i in range(len(points))]             # All nodes indices
        T = [i for i in range(1, nb_terminals + 1)]             # Terminals indices

        # Remove specified terminals from the list of terminals
        T = [t for t in T if t not in self.terminals_to_remove]

        T_extended = [0] + T                                    # Terminals indices with the root matrix
        R = [i for i in range(nb_terminals + 1, len(points))]   # Relays indices

        # Add the unserved terminals to the relays list
        #for t in self.terminals_to_remove:
        #    if t not in R:
        #        R.append(t)

        # endregion
        
        # Create the Pyomo model
        model = pyo.ConcreteModel()

        # region List of nodes
        model.N = pyo.Set(initialize=N_indices)
        model.T = pyo.Set(initialize=T)
        model.T_extended = pyo.Set(initialize=T_extended)
        model.R = pyo.Set(initialize=R)
        # endregion

        # region Links' score matrices (precomputed)
        model.C = pyo.Param(model.N, model.N, initialize=lambda _, i, j: float(self.score_matrix[0, i, j]), mutable=False, default=0.0)     # Capacity matrix
        model.PLR = pyo.Param(model.N, model.N, initialize=lambda _, i, j: float(self.score_matrix[1, i, j]), mutable=False, default=0.8)   # PLR matrix
        model.D = pyo.Param(model.N, model.N, initialize=lambda _, i, j: float(self.score_matrix[2, i, j]), mutable=False, default=1e12)    # Delay matrix
        # endregion

        # region Decision variables
        model.f0 = pyo.Var(model.N, model.N, domain=pyo.NonNegativeReals, bounds=(0, nb_terminals))     # Global flow matrix
        model.f = pyo.Var(model.T_extended, model.N, model.N, domain=pyo.Binary)                        # Flow matrix for each terminal (and the global topology)
        # endregion
        
        # region Auxiliary variables
        model.D_k = pyo.Var(model.T, domain=pyo.NonNegativeReals)        # Latency for each terminal
        # endregion

        # region PLR linearization variables
        model.plr_penalty = pyo.Var(model.T, domain=pyo.NonNegativeReals)  # PLR penalty for each terminal
        model.log_success = pyo.Var(model.T, domain=pyo.Reals, bounds=(min(plr_points), max(plr_points)))  # Logarithm of the success probability for each terminal
        # Approximation of the PLR function using piecewise linearization
        model.plr_piecewise = pyo.Piecewise(
            model.T,
            model.plr_penalty,
            model.log_success,
            pw_pts={k: plr_points for k in model.T},
            pw_constr_type='EQ',
            f_rule={k: plr_values for k in model.T},
            pw_repn='INC'
        )
        # endregion

        # region Fix non valid arcs
        for i in range(len(self.score_matrix[0])):
            for j in range(i, len(self.score_matrix[0][i])):
                if model.C[i, j] == 0 or model.PLR[i, j] == 1 or model.D[i, j] >= 1e10 or i == j:
                    model.f0[i, j].fix(0)
                    model.f0[j, i].fix(0)

                    for t in model.T_extended:
                        model.f[t, i, j].fix(0)
                        model.f[t, j, i].fix(0)
        # endregion
        
        # Define objective function
        def objective_rule(m):
            all_latencies = sum(m.D_k[t] for t in m.T)
            all_plr_penalties = sum(m.plr_penalty[t] for t in m.T)
            nb_used_relays = sum(m.f[0, i, r] for i in m.N for r in m.R if m.C[i, r] > 0)
            return self.alpha * all_latencies / D0 + self.beta * all_plr_penalties / (self.plr_max**2) + self.gamma * nb_used_relays / self.max_relays
        model.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

        ############# Define constraints #############

        # region basic constraints

        # Flow conservation constraints
        # Constraint the ratio of incoming and outgoing flows for each node over each terminal's tree
        def flow_conservation_rule(model, k, n):
            out_arcs = [model.f[k, n, j] for j in model.N if model.C[n, j] > 0] # Outgoing arcs from node n to all other nodes
            in_arcs = [model.f[k, i, n] for i in model.N if model.C[i, n] > 0]  # Incoming arcs from all other nodes to node n
            
            if not out_arcs and not in_arcs:
                return pyo.Constraint.Skip if n > nb_terminals else pyo.Constraint.Infeasible

            out_f = sum(out_arcs)
            in_f = sum(in_arcs)
            
            if n == 0:
                return out_f - in_f == 1                    # The root node has one more outgoing flow than incoming flow (it is the source of the flow)
            elif n == k or (k == 0 and n in model.T):
                return in_f - out_f == 1                    # The terminal node has one more incoming flow than outgoing flow (it is the sink of the flow)
            else: 
                return in_f - out_f == 0                    # All other nodes have the same amount of incoming and outgoing flows (they are relay nodes)
        model.flow_conservation = pyo.Constraint(model.T, model.N, rule=flow_conservation_rule)

        # Global flow sum (integer)
        # f0(i,j) count how many times the link (i,j) is used by the terminals
        def global_flow_sum_rule(model, i, j):
            return model.f0[i, j] == sum(model.f[k, i, j] for k in model.T)
        model.global_flow_sum = pyo.Constraint(model.N, model.N, rule=global_flow_sum_rule)

        # Global topology matrix (binary)
        # The global topology matrix is a binary matrix that indicates whether a link (i,j) is used by any terminal's tree.
        def global_topology_rule_1(model, i, j):
            return model.f[0, i, j] <= sum(model.f[k, i, j] for k in model.T)
        def global_topology_rule_2(model, i, j):
            return sum(model.f[k, i, j] for k in model.T) <= model.f[0, i, j] * nb_terminals        # Warning (change when re-writing)
        model.global_topology_1 = pyo.Constraint(model.N, model.N, rule=global_topology_rule_1)
        model.global_topology_2 = pyo.Constraint(model.N, model.N, rule=global_topology_rule_2)

        # input/output flow coupling
        # Constraint the incoming flow of each node (root, terminals, relays)
        def tree_structure_rule(model, k, n):
            incoming_L_vars = [model.f[k, i, n] for i in model.N if model.C[i, n] > 0]
            if not incoming_L_vars:
                return pyo.Constraint.Skip if n > nb_terminals else pyo.Constraint.Infeasible
            
            incoming_L_sum = sum(incoming_L_vars)
            if n == 0:
                return incoming_L_sum == 0                  # The root node has no incoming flow
            if n == k or (k == 0 and n in model.T):
                return incoming_L_sum == 1                  # The terminal node has exactly one incoming flow (in its personal tree)
            else:
                return incoming_L_sum <= 1                  # All other nodes have at most one incoming flow (they are relay nodes) (0 = not used, 1 = used)
        model.tree_structure = pyo.Constraint(model.T_extended, model.N, rule=tree_structure_rule)

        # Maximum number of child nodes
        def degree_out_rule(model, n):
            if n == 0:
                return pyo.Constraint.Skip
            
            outgoing_L_vars = [model.f[0, n, j] for j in model.N if model.C[n, j] > 0]

            if not outgoing_L_vars:
                return pyo.Constraint.Skip
            
            return sum(outgoing_L_vars) <= 2
        model.degree_out = pyo.Constraint(model.N, rule=degree_out_rule)

        # Prevent relay 2-cycles
        def prevent_relay_2cycles_rule(model, i, j):
            if (i < j and i > nb_terminals and j > nb_terminals and model.C[i, j] > 0):
                return model.f[0, i, j] + model.f[0, j, i] <= 1
            return pyo.Constraint.Skip
        model.prevent_relay_2cycles = pyo.Constraint(model.N, model.N, rule=prevent_relay_2cycles_rule)

        # endregion

        # Number of activated relays
        def max_nb_activated_relays_rule(model):
            return sum(model.f[0, i, r] for i in model.N for r in model.R if model.C[i, r] > 0) <= self.max_relays
        model.nb_activated_relays = pyo.Constraint(rule=max_nb_activated_relays_rule)

        # Linearized log plr 
        def log_plr_success_rule(model, k):
            return model.log_success[k] == sum(model.f[k, i, j] * math.log(1 - model.PLR[i, j]) for i in model.N for j in model.N if model.C[i, j] > 0)
        model.log_plr_success = pyo.Constraint(model.T, rule=log_plr_success_rule)

        # Maximum PLR per terminal
        def max_plr_rule(model, k):
            return model.log_success[k] >= math.log(1 - self.plr_max)
        model.max_plr = pyo.Constraint(model.T, rule=max_plr_rule)

        # Latency computation
        def latency_computation_rule(model, k):
            return model.D_k[k] == sum(model.f[k, i, j] * model.D[i, j] for i in model.N for j in model.N if model.C[i, j] > 0)
        model.latency_computation = pyo.Constraint(model.T, rule=latency_computation_rule)

        # Maximum congestion rate per link
        def max_congestion_rule(model, i, j):
            if model.C[i, j] == 0 or i == j:
                return pyo.Constraint.Skip
            return model.f0[i, j] <= rho_max * model.C[i, j] / C0
        model.max_congestion = pyo.Constraint(model.N, model.N, rule=max_congestion_rule)

        self.model = model

    # Solve the optimization problem using the given solver
    def solve(self, time_limit=600):
        self.solver = pyo.SolverFactory("highs")
        self.solver.options["time_limit"] = time_limit
        
        # Configure the persistent/new solver interface not to auto-load on failure
        if hasattr(self.solver, "config"):
            self.solver.config.load_solutions = False

        def run_solver():
            try:
                self.solution = self.solver.solve(self.model, tee=True)
            except Exception as e:
                # Catches NoFeasibleSolutionError or any other solver runtime crash
                print(f"Solver failed to find a solution: {e}")
                self.solution = None
                return False

            # Check the status from the results object
            if self.solution.solver.termination_condition != pyo.TerminationCondition.optimal:
                print("No solution found. Termination condition:", self.solution.solver.termination_condition)
                self.solution = None
                return False

            # If it was successful, explicitly load the solution back into the model variables
            if hasattr(self.solver, "load_vars"):
                self.solver.load_vars()
                
            self.build_solution_from_result()
            return True

        return run_solver()

    def build_solution_from_result(self):
        if self.solution is None:
            raise ValueError("No solution found. Please solve the model first.")
        
        relays = []
        links = []
        for i in self.model.N:
            for j in self.model.N:
                if i != j and self.model.f[0, i, j].value > 0.5:  # Assuming binary variables, check if the edge is selected
                    links.append((i, j))
                    if i > self.tree.get_nb_terminals() and i not in relays:
                        relays.append(i)
                    if j > self.tree.get_nb_terminals() and j not in relays:
                        relays.append(j)

        # Get final objective
        cost = round(pyo.value(self.model.objective),2)
        
        relays.sort()
        self.solution_out = {
            "relays": relays,
            "links": links,
            "cost": cost
        }

        self.solution_parameters = {
            "path_loss_exponent": self.path_loss_exponent,
            "max_relays": self.max_relays,
            "unit_throughput": self.unit_throughput,
            "plr_max": self.plr_max,
            "packet_size": self.packet_size,
            "max_utilization_rate": rho_max,
        }

        self.tree.set_solution(self.solution_out, self.solution_parameters)

    # region GETTERS
    ## GETTERS ##

    def get_model(self):
        return self.model
    
    def get_score_matrix(self):
        return self.score_matrix
    
    def get_solution(self):
        return self.solution
    
    def get_solver(self):
        return self.solver
    
    def get_tree(self):
        return self.tree
    # endregion

    # region string representation
    ## STRING REPRESENTATION ##

    def __str__(self):
        return f"Solver(tree={self.tree}, model={self.model}, score_matrix={self.score_matrix}, solution={self.solution}, solver={self.solver})"
    
    def __repr__(self):
        return self.__str__()
    # endregion
