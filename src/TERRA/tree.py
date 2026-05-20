from map import Map
import json
import matplotlib.pyplot as plt
from utils import *
import math

'''
# Type of plotting
EMPTY = 0
TERMINALS = 1
CANDIDATES = 2
CANDIDATES_EDGES = 3
SOLUTION = 4
'''

# Structure representing the full solution by itself
class solutionTree():
    def __init__(self, tree):
        self.tree = tree

        self.name = None                     # str
        self.map_size = None             # double
        self.obstacles = None           # [ [ (x,y) ] ] : double
        self.racine = None                   # (x,y) : double
        self.terminals = None           # [ (x,y) ] : double
        self.relays = None             # [ (x,y) ] : double
        self.links = None              # [ (int, int, double)]
        self.cost = None            # double

        self.update()
        
    
    def load(self, jsonSol):
        self.name = jsonSol["map_name"]
        self.map_size = jsonSol["map_size"]
        self.obstacles = jsonSol["obstacles"]
        self.racine = jsonSol["racine"]
        self.terminals = jsonSol["terminals"]
        self.relays = jsonSol["relays"]
        self.links = jsonSol["links"]
        self.cost = jsonSol["cost"]
    
    def save(self):
        output = {
            "map_name": self.name,
            "map_size": self.map_size,
            "obstacles": self.obstacles,
            "racine": self.racine,
            "terminals": self.terminals,
            "relays": self.relays,
            "links": self.links,
            "cost": self.cost
        }
        return output
    
    def update(self):
        self.name = self.tree.get_name()                     # str
        self.map_size = self.tree.get_map_size()             # double
        self.obstacles = self.tree.get_obstacles()           # [ [ (x,y) ] ] : double

        root = self.tree.get_root()
        if root != None:
            self.racine = self.tree.points[root]                   # (x,y) : double

        terminals = self.tree.get_terminals()
        if len(terminals) != 0:
            self.terminals = [self.tree.points[i] for i in terminals]           # [ (x,y) ] : double
        
        relays = self.tree.get_used_relays()
        if len(relays) != 0:
            self.relays = [self.tree.points[i] for i in relays]             # [ (x,y) ] : double

        links = self.tree.get_used_edges()
        #print(links)
        if len(links) != 0:
            self.links = self.update_edges(links)              # [ (int, int, double)]
        
        self.cost = self.tree.get_solution_cost()            # double
    
    # Update edges id with clean list
    def update_edges(self, links):
        tree_points = [self.racine] + self.terminals + self.relays
        print(len(tree_points), len(self.tree.points))
        print(tree_points[:10])
        print(self.tree.points[:10])
        print(links[:5])

        corrected_id = [-1] * len(self.tree.points)

        j = 0
        for id,p in enumerate(self.tree.points):
            if p == tree_points[j]:
                corrected_id[id] = j
                j += 1
            else:
                corrected_id[id] = -1
            if j >= len(tree_points):
                break
        print(corrected_id)
        
        tree_links = links.copy()

        for i in range(len(links)):
            tree_links[i] = (corrected_id[links[i][0]], corrected_id[links[i][1]])
        
        return tree_links

# The Tree class represents a tree in the TERRA environment.
class Tree:
    def __init__(self, map_name):
        self.map = Map(map_name)          # Map object
        
        self.points = None      # list of points, where each point is represented as a tuple (x, y)

        self.root = None        # id of the root point
        self.terminals = []   # list of ids of the terminal points
        self.candidates = []  # list of ids of the candidate points
        self.edges = []       # list of edges, where each edge is represented as a pair of ids
        self.used_edges = []   # list of edges that are used in the current solution, where each edge is represented as a pair of ids
        self.used_relays = []  # list of candidate points that are used as relays in the current solution, represented as a list of ids
        self.solution_cost = None   # cost of the current solution

        # Solution tree object
        self.solution_tree = solutionTree(self)

        self.previous_grid_parameters = [-1, None]
        self.previous_edges_parameters = [-1]

        self.fileIsWritten = [False, False, False, False]       # Terminals, Candidates, Edges, solution
        
        self.load_tree()
    
    # Load the tree data from the tree.json file in the map's directory
    def load_tree(self):
        # Load the tree data from the tree.json file in the map's directory
        self.map.load_mapdata()

        terminals = None
        candidates = None
        edges = None

        # Load root and terminals data from the terminals.json file in the map's directory (should exist)
        try:
            with open(f"{self.map.map_path}/terminals.json") as f:
                terminals = json.load(f)

            if terminals["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in terminals.json does not match the map name: {terminals['map_name']} != {self.map.get_name()}")
            
            self.root = 0
            self.terminals = list(range(1, len(terminals["terminals"])+1))

            self.fileIsWritten[0] = True
        except FileNotFoundError:
            raise FileNotFoundError(f"Terminals file not found in {self.map.map_path}")
        
        # Load candidate points data from the candidates.json file in the map's directory (could not exist)
        try:
            with open(f"{self.map.map_path}/candidates.json") as f:
                candidates = json.load(f)

            if candidates["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in candidates.json does not match the map name: {candidates['map_name']} != {self.map.get_name()}")
            
            self.candidates = list(range(1 + len(terminals["terminals"]), 1 + len(terminals["terminals"]) + len(candidates["candidates"])))
            self.fileIsWritten[1] = True
        except FileNotFoundError:
            pass
        
        # Load edges data from the edges.json file in the map's directory (could not exist)
        try:
            with open(f"{self.map.map_path}/edges.json") as f:
                edges = json.load(f)

            if edges["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in edges.json does not match the map name: {edges['map_name']} != {self.map.get_name()}")
            
            self.edges = edges["edges"]
            self.fileIsWritten[2] = True
        except FileNotFoundError:
            pass

        self.points = [terminals["racine"]] + terminals["terminals"]
        
        if candidates is not None:
            self.points += candidates["candidates"]
        
        # Load solution
        try:
            with open(f"{self.map.map_path}/solution.json") as f:
                solution = json.load(f)

            if solution["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in solution.json does not match the map name: {solution['map_name']} != {self.map.get_name()}")
            
            # Load data into solution tree object
            self.solution_tree.load(solution)
            
            #self.used_edges = solution["edges"]
            #self.used_relays = solution["candidates"]
            #self.solution_cost = solution["solution_cost"]
            self.fileIsWritten[3] = True
        except FileNotFoundError:
            pass
    
    # Save to file
    # Map : map data
    # Tree : Terminals, candidates, edges, solution
    def save_tree(self):
        # Save the map data
        self.map.save_mapdata()

        # Save the tree data
        if not self.fileIsWritten[0]:
            terminals_data = {
                "map_name": self.map.get_name(),
                "racine": self.points[0],
                "terminals": self.points[1:]
            }
            with open(f"{self.map.map_path}/terminals.json", "w") as f:
                json.dump(terminals_data, f, indent=2)
            self.fileIsWritten[0] = True
        
        if not self.fileIsWritten[1]:
            candidates_data = {
                "map_name": self.map.get_name(),
                "candidates": self.get_candidates_positions()
            }
            with open(f"{self.map.map_path}/candidates.json", "w") as f:
                json.dump(candidates_data, f, indent=2)
            self.fileIsWritten[1] = True
        
        if not self.fileIsWritten[2]:
            edges_data = {
                "map_name": self.map.get_name(),
                "edges": self.edges
            }
            with open(f"{self.map.map_path}/edges.json", "w") as f:
                json.dump(edges_data, f, indent=2)
            self.fileIsWritten[2] = True

        if not self.fileIsWritten[3]:
            solution_data = self.solution_tree.save()
            with open(f"{self.map.map_path}/solution.json", "w") as f:
                json.dump(solution_data, f, indent=2)
            self.fileIsWritten[3] = True

           
    # Compute the figures and axes of the tree
    def plot(self, bool_values=[True, True, False, False, False]):
        self.map.compute_fig_ax(bool_values[0])

        labels = {"root": "Root", "terminal": "Terminal", "candidate": "Candidate", "other": "Other", "used_edge": "Used Edge", "edge": "Edge"}

        # Draw the points of the tree, with different colors for the root, terminal, candidate and other points
        for idx, point in enumerate(self.points):
            if idx == self.root and bool_values[1]:
                circle = plt.Circle(point, radius=0.5, color='blue', zorder=5, label=labels["root"])
                labels["root"] = "_nolegend_"  # only show the label for the root point
                self.map.ax.add_patch(circle)
            elif idx in self.terminals and bool_values[1]:
                circle = plt.Circle(point, radius=0.5, color='red', zorder=5, label=labels["terminal"])
                labels["terminal"] = "_nolegend_"  # only show the label for the terminal point
                self.map.ax.add_patch(circle)
            elif idx in self.candidates and (bool_values[2] or (bool_values[4] and idx in self.used_relays)):
                circle = plt.Circle(point, radius=0.5, color='green', zorder=5, label=labels["candidate"])
                labels["candidate"] = "_nolegend_"  # only show the label for the candidate point
                self.map.ax.add_patch(circle)
            #elif False:
            #    circle = plt.Circle(point, radius=0.3, color='black', zorder=5, label=labels["other"])
            #    labels["other"] = "_nolegend_"  # only show the label for the other points
            #    self.map.ax.add_patch(circle)
        
        # Draw the edges of the tree, with different colors for the used and unused edges
        if bool_values[3]:
            for edge in self.edges:
                p1 = self.points[edge[0]]
                p2 = self.points[edge[1]]
                if edge[2] >= 1e10:
                    continue
                    
                line = plt.Line2D([p1[0], p2[0]], [p1[1], p2[1]], color='lightgreen', linewidth=0.5, zorder=3, label=labels["edge"])
                self.map.ax.add_patch(line)
                labels["edge"] = "_nolegend_"  # only show the label for the edges
        
        if bool_values[4]:
            for edge in self.used_edges:
                p1 = self.points[edge[0]]
                p2 = self.points[edge[1]]
                line = plt.Line2D([p1[0], p2[0]], [p1[1], p2[1]], color='orange', linewidth=2, zorder=4, label=labels["used_edge"])
                self.map.ax.add_patch(line)
                labels["used_edge"] = "_nolegend_"  # only show the label for the used edges


        #plt.grid(True, linestyle='--', alpha=0.3)
        #plt.legend()
        #plt.show()

    def generate_discrete_grid(self, grid_size, include_obstacles=True):
        if self.previous_grid_parameters == [grid_size, include_obstacles]:
            return
        self.previous_grid_parameters = [grid_size, include_obstacles]
        self.fileIsWritten[1:] = [False] * 3

        # Generate a discrete grid of points in the map, with a given grid size
        self.points = self.points[:1 + len(self.terminals)]
        points = []

        # Clear existing candidates, edges and solution
        self.candidates = []
        self.edges = []
        self.used_edges = []
        self.used_relays = []
        self.solution_cost = None
        
        if include_obstacles:
            for obs in self.map.get_obstacles():
                for vertex in obs:
                    points.append(vertex)

        for x in range(0, int(self.map.get_map_size()) + 1, grid_size):
            for y in range(0, int(self.map.get_map_size()) + 1, grid_size):
                if not is_point_in_obstacle((x, y), self.map.get_obstacles()) and min_dist((x, y), points + self.points) > grid_size/5:
                    points.append((x, y))
        
        self.candidates = list(range(1 + len(self.terminals), 1 + len(self.terminals) + len(points)))
        #print(f"Generate candidates: {self.candidates}")
        self.points += points

    # Compute the edges of the tree, where each edge is represented as a pair of ids
    def compute_edges(self, dMax = 1e10):
        if self.previous_edges_parameters == [dMax]:
            return
        self.previous_edges_parameters = [dMax]
        self.fileIsWritten[2:] = [False] * 2

        # Clear existing edges and solution
        self.edges = []
        self.used_edges = []
        self.used_relays = []
        self.solution_cost = None

        edges = []
        for i in range(len(self.points)):
            p1 = self.points[i]
            for j in range(i+1, len(self.points)):
                p2 = self.points[j]
                if not is_line_obstructed(p1, p2, self.map.get_obstacles()):
                    dist = compute_distance(p1, p2)
                    edges.append((i, j, dist if dist <= dMax else 1e12))
        self.edges = edges

    def set_solution(self, solution):
        self.fileIsWritten[3] = False
        self.used_edges = solution["links"]
        self.used_relays = solution["relays"]    
        self.solution_cost = solution["cost"]

        print(f"Used edges: {self.used_edges}")
        print(f"Used relays: {self.used_relays}")
        print(f"Solution cost: {self.solution_cost}")

        self.solution_tree.update()

        #self.used_edges = []  
        #for edge in self.edges:
        #    if (edge[0], edge[1]) in solution or (edge[1], edge[0]) in solution:
        #        self.used_edges.append(edge)

    # Local correction following a force model
    def local_correction(self, dt, tMax, dmin=10, dmax=30, fMax=1000, k=0.0001):

        def compute_forces(p1, p2, dmin, dmax, fMax):   # Forces from p1 towards p2
            dist = compute_distance(p1, p2)

            X = (dist - dmin) / (dmax - dmin)
            
            if X >= 1:
                mag = fMax
            else:
                mag = X * fMax

            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            return [mag * math.cos(angle), mag * math.sin(angle)]

        fixed_points_id = [self.root] + self.terminals
        mobile_points_id = self.used_relays
        all_points_id = fixed_points_id + mobile_points_id

        fixed_points = [self.points[i] for i in fixed_points_id]
        mobile_points = [self.points[i] for i in mobile_points_id]
        all_points = fixed_points + mobile_points

        link_to_mobile_id = [[] for _ in range(len(mobile_points))]
        for e in self.used_edges:
            e0 = all_points_id.index(e[0])
            e1 = all_points_id.index(e[1])
            if (e[0] in mobile_points_id):
                link_to_mobile_id[mobile_points_id.index(e[0])].append(e1)
            if (e[1] in mobile_points_id):
                link_to_mobile_id[mobile_points_id.index(e[1])].append(e0)

        # Initialize forces
        forces = [[0, 0] for _ in range (len(mobile_points_id))]

        #print(fixed_points)
        #print(mobile_points)
        #print(link_to_mobile_id)

        for t in range(dt, tMax + dt, dt):
            # Compute forces
            for id, p in enumerate(mobile_points):
                forces[id] = [0, 0]
                for link in link_to_mobile_id[id]:
                    forces[id] = [a + b for a, b in zip(forces[id], compute_forces(p, all_points[link], dmin, dmax, fMax))]

            # Compute new pose
            new_pos = []
            for id, p in enumerate(mobile_points):
                new_pos.append([p[0] + forces[id][0] * k, p[1] + forces[id][1] * k])
            
            corrected_pos = [p for p in new_pos]
            # Check new pos, with LOS and obstacles
            for id, p in enumerate(new_pos):
                stop = False
                if is_point_in_obstacle(p, self.map.get_obstacles()):
                    stop = True

                for id2 in link_to_mobile_id[id]:

                    if id2 >= len(fixed_points):
                        p2 = new_pos[id2 - len(fixed_points)]
                    else:
                        p2 = all_points[id2]

                    if is_line_obstructed(p, p2, self.map.get_obstacles()):
                        stop = True
                        break
                
                if stop:
                    corrected_pos[id] = mobile_points[id]
                else:
                    corrected_pos[id] = new_pos[id]
            
            for id, p in enumerate(corrected_pos):
                new_pos[id] = corrected_pos[id]

            # Update position
            for id in range(len(mobile_points)):
                mobile_points[id] = [new_pos[id][0], new_pos[id][1]]

        # Update relays positions
        for id, p in enumerate(mobile_points_id):
            self.points[p] = mobile_points[id]


    #region Getter

    # Get the size of the map
    def get_map_size(self):
        return self.map.get_map_size()
    
    # Get the list of obstacles, where each obstacle is represented as a list of vertices (x, y)
    def get_obstacles(self):
        return self.map.get_obstacles()
    
    # Get the name of the map
    def get_name(self):
        return self.map.get_name()

    # Get the map associated with the tree
    def get_map(self):
        return self.map
    
    # Get the points of the tree, represented as a list of points
    def get_points(self):
        return self.points
    
    # Get the id of the root point
    def get_root(self):
        return self.root
    
    def get_terminals(self):
        return self.terminals
    
    # Get the edges of the tree, where each edge is represented as a pair of ids
    def get_edges(self):
        return self.edges
    
    # Get the candidate points of the tree, represented as a list of ids
    def get_candidates(self):
        return self.candidates
    
    def get_candidates_positions(self):
        return [self.points[i] for i in self.candidates]
    
    # Get the used edges of the tree
    def get_used_edges(self):
        return self.used_edges
    
    # Get the used relaus of the tree
    def get_used_relays(self):
        return self.used_relays
    # Get the solution cost
    def get_solution_cost(self):
        return self.solution_cost
    
    # Get the number of terminals in the tree
    def get_nb_terminals(self):
        return len(self.terminals)
    #endregion

    # region str representation

    # String representation of the tree for debugging purposes
    def __str__(self):
        return f"Tree(map={self.map}, points={self.points}, root={self.root}, terminals={self.terminals}, candidates={self.candidates}, edges={self.edges}, used_edges={self.used_edges})"
    
    # Use the string representation of the tree for the official representation of the tree
    def __repr__(self):
        return self.__str__()
    #endregion