from map import Map
import json
import matplotlib.pyplot as plt
from utils import *

# Type of plotting
EMPTY = 0
TERMINALS = 1
CANDIDATES = 2
CANDIDATES_EDGES = 3
SOLUTION = 4

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
            self.terminals = range(1, len(terminals["terminals"])+1)
        except FileNotFoundError:
            raise FileNotFoundError(f"Terminals file not found in {self.map.map_path}")
        
        # Load candidate points data from the candidates.json file in the map's directory (could not exist)
        try:
            with open(f"{self.map.map_path}/candidates.json") as f:
                candidates = json.load(f)

            if candidates["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in candidates.json does not match the map name: {candidates['map_name']} != {self.map.get_name()}")
            
            self.candidates = range(1 + len(terminals["terminals"]), 1 + len(terminals["terminals"]) + len(candidates["candidates"]))
        except FileNotFoundError:
            pass
        
        # Load edges data from the edges.json file in the map's directory (could not exist)
        try:
            with open(f"{self.map.map_path}/edges.json") as f:
                edges = json.load(f)

            if edges["map_name"] != self.map.get_name():
                raise ValueError(f"Map name in edges.json does not match the map name: {edges['map_name']} != {self.map.get_name()}")
            
            self.edges = edges["edges"]
        except FileNotFoundError:
            pass

        self.points = [terminals["racine"]] + terminals["terminals"]
        
        if candidates is not None:
            self.points += candidates["candidates"]
           
    # Compute the figures and axes of the tree
    def plot(self, type=TERMINALS):
        self.map.compute_fig_ax()

        labels = {"root": "Root", "terminal": "Terminal", "candidate": "Candidate", "other": "Other", "used_edge": "Used Edge", "edge": "Edge"}

        # Draw the points of the tree, with different colors for the root, terminal, candidate and other points
        for idx, point in enumerate(self.points):
            if idx == self.root and type >= TERMINALS:
                circle = plt.Circle(point, radius=0.5, color='blue', zorder=5, label=labels["root"])
                labels["root"] = "_nolegend_"  # only show the label for the root point
                self.map.ax.add_patch(circle)
            elif idx in self.terminals and type >= TERMINALS:
                circle = plt.Circle(point, radius=0.5, color='red', zorder=5, label=labels["terminal"])
                labels["terminal"] = "_nolegend_"  # only show the label for the terminal point
                self.map.ax.add_patch(circle)
            elif idx in self.candidates and type >= CANDIDATES:
                circle = plt.Circle(point, radius=0.5, color='green', zorder=5, label=labels["candidate"])
                labels["candidate"] = "_nolegend_"  # only show the label for the candidate point
                self.map.ax.add_patch(circle)
            elif type > EMPTY:
                circle = plt.Circle(point, radius=0.3, color='black', zorder=5, label=labels["other"])
                labels["other"] = "_nolegend_"  # only show the label for the other points
                self.map.ax.add_patch(circle)
        
        # Draw the edges of the tree, with different colors for the used and unused edges
        for edge in self.edges:
            p1 = self.points[edge[0]]
            p2 = self.points[edge[1]]
            if edge[2] >= 1e10:
                continue

            if edge in self.used_edges and type >= SOLUTION:
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='orange', linewidth=2, zorder=4, label=labels["used_edge"])
                labels["used_edge"] = "_nolegend_"  # only show the label for the used edges
            elif type >= CANDIDATES_EDGES:
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='lightgreen', linewidth=0.5, zorder=3, label=labels["edge"])
                labels["edge"] = "_nolegend_"  # only show the label for the edges

        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend()
        plt.show()

    def generate_discrete_grid(self, grid_size, include_obstacles=True):
        # Generate a discrete grid of points in the map, with a given grid size
        points = []
        
        if include_obstacles:
            for obs in self.map.get_obstacles():
                for vertex in obs:
                    points.append(vertex)

        for x in range(0, int(self.map.get_map_size()) + 1, grid_size):
            for y in range(0, int(self.map.get_map_size()) + 1, grid_size):
                if not is_point_in_obstacle((x, y), self.map.get_obstacles()) and min_dist((x, y), points + self.points) > grid_size/5:
                    points.append((x, y))
        
        self.candidates = range(1 + len(self.terminals), 1 + len(self.terminals) + len(points))
        self.points += points

    # Compute the edges of the tree, where each edge is represented as a pair of ids
    def compute_edges(self, cMax = 1e10):
        edges = []
        for i in range(len(self.points)):
            p1 = self.points[i]
            for j in range(i+1, len(self.points)):
                p2 = self.points[j]
                if not is_line_obstructed(p1, p2, self.map.get_obstacles()):
                    cost = compute_distance(p1, p2)
                    edges.append((i, j, cost if cost <= cMax else 1e12))
        self.edges = edges

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
    
    # Get the used edges of the tree
    def get_used_edges(self):
        return self.used_edges
    
    def get_nb_terminals(self):
        return len(self.terminals)
    
    # String representation of the tree for debugging purposes
    def __str__(self):
        return f"Tree(map={self.map}, points={self.points}, root={self.root}, terminals={self.terminals}, candidates={self.candidates}, edges={self.edges}, used_edges={self.used_edges})"
    
    # Use the string representation of the tree for the official representation of the tree
    def __repr__(self):
        return self.__str__()