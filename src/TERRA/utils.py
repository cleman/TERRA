import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
import random
import math


# Compute the minimum distance from a point to a list of points
def min_dist(point, points):
    min_dist = float('inf')
    for p in points:
        dist = (point[0] - p[0])**2 + (point[1] - p[1])**2
        if dist < min_dist:
            min_dist = dist
    return min_dist**0.5

# Check if a point is in an obstacle
def is_point_in_obstacle(point, obstacles):
    # Check if a point is in an obstacle
    for obs in obstacles:
        polygon = plt.Polygon(obs)
        if polygon.contains_point(point):
            return True
    return False

def line_intersects_polygon(p1, p2, polygon):
    # décalage de 0.01 pour éviter les problèmes de précision (p1 vers p2 et p2 vers p1)
    delta = (p2[0] - p1[0], p2[1] - p1[1])
    epsilon = 0.01
    p1_shifted = (p1[0] + epsilon * delta[0], p1[1] + epsilon * delta[1])
    p2_shifted = (p2[0] - epsilon * delta[0], p2[1] - epsilon * delta[1])
    line = LineString([p1_shifted, p2_shifted])
    poly = Polygon(polygon)
    return line.intersects(poly)

def compute_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def is_line_obstructed(p1, p2, obstacles):
    for obs in obstacles:
        if line_intersects_polygon(p1, p2, obs):
            return True
    return False

# Function to check if two polygons overlap
def polygons_overlap(polygon1, polygon2):
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    return poly1.intersects(poly2)

# Function to generate a random polygon without overlap
def generate_obstacle(map_size, max_vertices, max_size, existing_obstacles):
    for _ in range(100):  # Try up to 100 times to find a non-overlapping polygon
        num_vertices = random.randint(3, max_vertices)  # At least 3 vertices for a polygon
        center_x = random.uniform(0, map_size)
        center_y = random.uniform(0, map_size)
        radius = random.uniform(0.2*max_size, max_size)

        vertices = []
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            x = center_x + radius * random.uniform(0.5, 1.0) * math.cos(angle)
            y = center_y + radius * random.uniform(0.5, 1.0) * math.sin(angle)
            vertices.append((x, y))

        # Check for overlap
        if not any(polygons_overlap(vertices, obs) for obs in existing_obstacles):
            return vertices

    raise ValueError("Could not place a non-overlapping polygon after 100 attempts")

############# COST TO CHANGE #############
def fcost(dist):
    dist_unit = 10.0
    k_coef = 1
    C0 = 2
    dist_norm = dist / dist_unit
    return k_coef * dist_norm**2 + C0

def compute_solution_cost(tree):
    cost = 0
    for edge in tree.get_used_edges():          # ← used_edges, not edges
        p1 = tree.points[edge[0]]
        p2 = tree.points[edge[1]]
        dist = compute_distance(p1, p2)
        cost += fcost(dist)
    return cost