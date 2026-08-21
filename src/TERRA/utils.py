import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
import random
import math
import numpy as np


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

def compute_solution_cost_network(tree, chains, weights = [0.8, 0.1, 0.1], ref_values = [0.05, 0.05], limit_values = [5e6, 0.02]):
    print(f"Computing solution cost: chain [0/{len(chains)}]", end="\r")

    cost = 0
    for i, chain in enumerate(chains):
        print(f"Computing solution cost: chain [{i+1}/{len(chains)}]", end="\r")
        Delay = 0
        PLR = 1
        C_bottleneck = float('inf')
        if chain is None or len(chain) == 0:
            raise ValueError("Chains cannot be None or empty")
        for i in range(len(chain)):
            p1 = tree.points[chain[i][0]]
            p2 = tree.points[chain[i][1]]
            dist = compute_distance(p1, p2)
            C, PLR_ij, D_ij = C_PLR_D(dist)

            if C < C_bottleneck:
                C_bottleneck = C

            Delay += D_ij
            PLR *= (1 - PLR_ij)

        PLR = 1 - PLR  # Convert to packet loss rate

        # Check for communication constraints
        if C_bottleneck < limit_values[0] or PLR > limit_values[1]:
            print(f"Warning: Communication constraints violated for chain {chain}. C_bottleneck: {C_bottleneck}, PLR: {PLR}")
            k_coeff = 2
        else:
            k_coeff = 1

        cost += (weights[0] * Delay/ref_values[0] + weights[1] * PLR/ref_values[1]) * k_coeff

    print(f"Computing solution cost: chain [{len(chains)}/{len(chains)}] - Done", end="\r")
    return cost

# Product of the elements of a list
def product(lst):
    result = 1
    for num in lst:
        result *= num
    return result

# Compute capacity, PLR and delay of a chain
def compute_chain_metrics(tree, chain, C_min=5e6, n=3.5, l=8000):
    Delay = 0
    PLR = 1
    C_bottleneck = float('inf')

    if chain is None or len(chain) == 0:
        raise ValueError("Chains cannot be None or empty")

    for i in range(len(chain)):
        p1 = tree.points[chain[i][0]]
        p2 = tree.points[chain[i][1]]
        dist = compute_distance(p1, p2)
        C, PLR_ij, D_ij = C_PLR_D(dist, C_min=C_min, n=n, l=l)

        print(f"  edge {chain[i]}: dist={dist:.2f}m  C={C/1e6:.2f}Mbps  PLR_ij={PLR_ij}")  # <- AJOUT
        if C < C_bottleneck:
            C_bottleneck = C

        Delay += D_ij
        PLR *= (1 - PLR_ij)

    PLR = 1 - PLR  # Convert to packet loss rate

    return C_bottleneck, PLR, Delay

########### Parameters to move to a config file ###########
B = 20e6        # Bandwidth in Hz
Px = 20         # Transmit power in dBm
N = -90        # Noise power in dBm
PL_d0 = 40        # Path loss at reference distance d0 in dB
d0 = 1.0        # reference distance for PLR calculation

def C_PLR_D(dist, C_min=5e6, n=3.5, l=8000):
    d = dist * 1        # Scale factor to adapt current configuration to something more realistic (for dev only-before creating an adapted map)

    # Path Loss
    P_loss = PL_d0 + 10 * n * np.log10(d/d0)

    # Signal to Noise Ratio (SNR)
    SNR = Px - P_loss - N

    # Capacity (Shannon-Hartley theorem)
    C = B * np.log2(1 + 10**(SNR/10))

    # Packet Loss Rate (PLR)
    #PLR = 1 - (C / C_min) if C < C_min else 0.0
    BER = 0.5 * math.erfc(np.sqrt(10**(SNR/10)))
    PLR = 1 - (1 - BER)**l if C >= C_min else 1.0
    PLR = min(max(PLR, 0.0), 1.0)  # Ensure PLR is between 0 and 1

    # Latency (in seconds)
    L = l / C if C > 0 else float('inf')

    return C, PLR, L