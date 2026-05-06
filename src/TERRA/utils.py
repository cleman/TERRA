import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon

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
    epsilon = 0.1
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

############# COST TO CHANGE #############
def fcost(dist):
    dist_unit = 10.0
    k_coef = 1
    C0 = 2
    dist_norm = dist / dist_unit
    return k_coef * dist_norm**2 + C0