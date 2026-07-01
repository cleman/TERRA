# pragma once
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json
from utils import generate_obstacle

from copy import deepcopy

# The Map class represents a map in the TERRA environment. It loads the map data from a JSON file and provides methods to access the map size, obstacles, and name. It also provides a method to get the figures and axes for plotting the map.
class Map:
    # Initialize the map by loading the map data from the mapdata.json file in the map's directory
    def __init__(self, name):
        self.name = name
        self.map_path = f"data/maps/{self.name}"
        self.map_size = None
        self.obstacles = None
        self.load_mapdata()     # load map_size, obstacles
        self.mapdataIsWritten = False

        self.map_fig = None
        self.map_figIsWritten = False
    
    # Load map data from the mapdata.json file in the map's directory
    def load_mapdata(self):
        # Check if the mapdata.json file exists
        try:
            # Load the mapdata.json file
            with open(f"{self.map_path}/mapdata.json") as f:
                mapdata = json.load(f)
            
            if mapdata["map_name"] != self.name:
                raise ValueError(f"Map name in mapdata.json does not match the map name: {mapdata['map_name']} != {self.name}")
            
            self.map_size = mapdata["map_size"]     # double
            self.obstacles = mapdata["obstacles"]   # list of list of vertices (x, y)
            
            self.mapdataIsWritten = True
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Mapdata file not found in {self.map_path}")
        
        # Check if the map figure exists, if not, set self.map_figIsWritten to False
        if not os.path.exists(f"{self.map_path}/map_fig.png"):
            self.map_figIsWritten = False
    
    # Save map data
    def save_mapdata(self):
        # Save map figure
        if self.map_fig is not None and not self.map_figIsWritten:
            self.map_fig.savefig(f"{self.map_path}/map_fig_env.png")
            self.map_figIsWritten = True

        # Save map data
        if self.mapdataIsWritten:
            return
        if self.name is None:
            raise ValueError("Map name is None")
        if self.map_size is None:
            raise ValueError("Map size is None")
        if self.obstacles is None:
            raise ValueError("Obstacles are None")
        
        # Check if the map directory exists, if not create it
        if not os.path.exists(self.map_path):
            os.makedirs(self.map_path)

        mapdata = {
            "map_name": self.name,
            "map_size": self.map_size,
            "obstacles": self.obstacles
        }
        with open(f"{self.map_path}/mapdata.json", "w") as f:
            json.dump(mapdata, f, indent=2)

        self.mapdataIsWritten = True
    
    # Get the size of the map
    def get_map_size(self):
        return self.map_size
    
    # Get the list of obstacles, where each obstacle is represented as a list of vertices (x, y)
    def get_obstacles(self):
        return self.obstacles
    
    # Set the name of the map
    def set_name(self, name):
        self.name = name
        self.map_path = f"data/maps/{self.name}"
        self.mapdataIsWritten = False  # Mark map data as not written since the name has changed
    
    # Get the name of the map
    def get_name(self):
        return self.name
    
    # String representation of the map for debugging purposes
    def __str__(self):
        return f"Map(name={self.name}, map_size={self.map_size}, obstacles={self.obstacles})"
    
    # Use the string representation of the map for the official representation of the map
    def __repr__(self):
        return self.__str__()
    
    # Compute the figures and axes of the map for plotting purposes
    def compute_fig_ax(self, bool_value, include_obstacles=True):        
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, self.map_size)
        ax.set_ylim(0, self.map_size)
        
        # Plot the obstacles
        obstacleLabel = "Obstacle"
        if bool_value:
            for obs in self.obstacles:
                polygon = Polygon(obs, closed=True, fill=True, edgecolor='black', facecolor='gray', label=obstacleLabel)
                obstacleLabel = "_nolegend_"  # only show the label for the first obstacle
                ax.add_patch(polygon)
        
        self.fig = fig
        self.ax = ax
    
    # Generate a random map with a given size, number of obstacles and maximum size of obstacles
    def generate_obstacles(self, map_size, num_obstacles, max_size):
        
        self.obstacles = []
        for _ in range(num_obstacles):
            self.obstacles.append(generate_obstacle(map_size, 8, max_size, self.obstacles))
        
        self.racine = None  # Clear racine when generating new obstacles
        self.terminals = []  # Clear terminals when generating new obstacles

        self.mapDataIsWritten = False
        self.map_figIsWritten = False
    
    def update_map_fig(self):
        self.map_fig = deepcopy(self.fig)