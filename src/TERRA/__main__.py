from tree import Tree
from solver import Solver

import matplotlib.pyplot as plt

def main():
    # Create a tree for the "map2" map
    tree = Tree("map2")

    #print(tree.map)
    #print(tree)
    tree.generate_discrete_grid(grid_size=20, include_obstacles=True)
    tree.compute_edges(dMax=50)
    #print(f"Number of edges: {len(tree.get_edges())}")
    #tree.plot(2)
    #tree.plot(3)

    solver = Solver(tree)
    solver.solve(solver_name="appsi_highs", time_limit=600)
    print("#" * 50)
    print("SOLUTION")
    print("#" * 50)
    print(solver.get_solution())

    tree.local_correction(10, 20, dmin=10, dmax=30, fMax=1000, k=0.001)

    # Plot fig
    tree.plot([True, True, True, True, True])
    fig, ax = tree.map.fig, tree.map.ax
    plt.show()


if __name__ == "__main__":
    main()