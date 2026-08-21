from utils import fcost, compute_distance
from tree import Tree
import pyomo.environ as pyo
import time
import sys
import numpy as np

class Solver:
    def __init__(self, tree, max_relays=10):
        self.tree = tree
        self.max_relays = max_relays

        self.model = None
        self.solver = None
        self.solution = None
        self.cost_matrix = None

        tree.solver_used = 1  # Mark that this solver is used for the current solution

        self.build_cost_matrix()

        self.build_model()
    
    # Build the cost matrix for the given tree
    def build_cost_matrix(self):
        # Initialize the cost matrix with a large value (infinity) for non-existing edges and 0 for diagonal elements
        cost_matrix = np.full((len(self.tree.points), len(self.tree.points)), 1e12, dtype=float)

        # 
        for e in self.tree.edges:
            if e[2] > 1e10:
                continue
            cost = fcost(e[2])
            cost_matrix[e[0], e[1]] = cost
            cost_matrix[e[1], e[0]] = cost

        self.cost_matrix = cost_matrix

    # Build the optimization model for the given tree
    def build_model(self):
        points = self.tree.points
        nb_terminals = self.tree.get_nb_terminals()

        N_indices = [i for i in range(len(points))]
        n = len(points)
        model = pyo.ConcreteModel()

        model.N = pyo.Set(initialize=N_indices)
        model.D = pyo.Param(model.N, model.N, initialize=lambda m, i, j: float(self.cost_matrix[i][j]), mutable=False, default=1e12)

        model.L = pyo.Var(model.N, model.N, domain=pyo.Binary)
        model.f = pyo.Var(model.N, model.N, domain=pyo.NonNegativeReals, bounds=(0, nb_terminals))
        #model.f = pyo.Var(model.N, model.N, domain=pyo.Integers, bounds=(0, nb_terminals))

        # Fix non valid arcs
        for i in range(len(self.cost_matrix)):
            for j in range(i, len(self.cost_matrix[i])):
                if self.cost_matrix[i][j] > 1e10 or i == j:
                    model.L[i, j].fix(0)
                    model.f[i, j].fix(0)
                
                    if i != j:
                        model.L[j, i].fix(0)
                        model.f[j, i].fix(0)

        # Define objective function
        def objective_rule(m):
            return sum(m.D[i, j] * m.L[i, j] for i in model.N for j in model.N if i != j and m.D[i, j] < 1e10)   # Longer to build the model but faster to solve
        model.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

        ############# Define constraints #############

        # Flow conservation constraints
        def flow_conservation_rule(model, n):
            out_arcs = [model.f[n,j] for j in model.N if model.D[n, j] < 1e10]
            in_arcs = [model.f[i,n] for i in model.N if model.D[i, n] < 1e10]
            
            if not out_arcs and not in_arcs:
                return pyo.Constraint.Skip if n > nb_terminals else pyo.Constraint.Infeasible

            out_f = sum(out_arcs)
            in_f = sum(in_arcs)
            
            if n == 0: return out_f - in_f == nb_terminals
            elif n <= nb_terminals: return in_f - out_f == 1
            else: return in_f - out_f == 0
        model.flow_conservation = pyo.Constraint(model.N, rule=flow_conservation_rule)

        # Coupling constraints between flow and link variables
        def flow_link_coupling_rule(model, i, j):
            if model.D[i, j] >= 1e10 or i == j:
                return pyo.Constraint.Skip
            return model.f[i, j] <= model.L[i, j] * nb_terminals
        model.flow_link_coupling = pyo.Constraint(model.N, model.N, rule=flow_link_coupling_rule)

        def link_flow_coupling_rule(model, i, j):
            if model.D[i, j] >= 1e10 or i == j:
                return pyo.Constraint.Skip
            return model.L[i, j] <= model.f[i, j]
        model.link_flow_coupling = pyo.Constraint(model.N, model.N, rule=link_flow_coupling_rule)

        def tree_structure_rule(model, n):
            #if n == 0: return pyo.Constraint.Skip 
            incoming_L_vars = [model.L[i, n] for i in model.N if model.D[i, n] < 1e10]
            if not incoming_L_vars:
                return pyo.Constraint.Skip if n > nb_terminals else pyo.Constraint.Infeasible
            
            incoming_L_sum = sum(incoming_L_vars)
            if n == 0:
                return incoming_L_sum == 0
            return incoming_L_sum == 1 if n <= nb_terminals else incoming_L_sum <= 1
        model.tree_structure = pyo.Constraint(model.N, rule=tree_structure_rule)

        def degree_out_rule(model, n):
            #if n == 0: return pyo.Constraint.Skip
            outgoing_L_vars = [model.L[n, j] for j in model.N if model.D[n, j] < 1e10]
            if not outgoing_L_vars: return pyo.Constraint.Skip
            return sum(outgoing_L_vars) <= 2
        model.degree_out = pyo.Constraint(model.N, rule=degree_out_rule)

        # Number of activated relays constraints
        def nb_activated_relays_rule(model):
            return sum(model.L[i, j] for i in model.N for j in model.N if j > nb_terminals and model.D[i, j] < 1e10) <= self.max_relays
        model.nb_activated_relays = pyo.Constraint(rule=nb_activated_relays_rule)

        def prevent_relay_2cycles_rule(model, i, j):
            if (i < j and i > nb_terminals and j > nb_terminals and model.D[i, j] < 1e10):
                return model.L[i, j] + model.L[j, i] <= 1
            return pyo.Constraint.Skip
        model.prevent_relay_2cycles = pyo.Constraint(model.N, model.N, rule=prevent_relay_2cycles_rule)

        self.model = model

    # Solve the optimization problem using the given solver
    def solve(self, solver_name="appsi_highs", time_limit=600):
        self.solver = pyo.SolverFactory(solver_name)
        self.solver.options["time_limit"] = time_limit

        def run_solver():
            self.solution = self.solver.solve(self.model, tee=True)
            self.build_solution_from_result()

        run_solver()


    def build_solution_from_result(self):
        if self.solution is None:
            raise ValueError("No solution found. Please solve the model first.")
        
        relays = []
        links = []
        for i in self.model.N:
            for j in self.model.N:
                if i != j and self.model.L[i, j].value > 0.5:  # Assuming binary variables, check if the edge is selected
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

        self.tree.set_solution(self.solution_out)

    # region GETTERS
    ## GETTERS ##

    def get_model(self):
        return self.model
    
    def get_cost_matrix(self):
        return self.cost_matrix
    
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
        return f"Solver(tree={self.tree}, model={self.model}, cost_matrix={self.cost_matrix}, solution={self.solution}, solver={self.solver})"
    
    def __repr__(self):
        return self.__str__()
    # endregion

