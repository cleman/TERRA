from tree import Tree

def main():
    # Create a tree for the "map2" map
    tree = Tree("map2")

    #print(tree.map)
    #print(tree)
    tree.generate_discrete_grid(grid_size=20, include_obstacles=True)
    tree.compute_edges(cMax=30)
    print(f"Number of edges: {len(tree.get_edges())}")
    #tree.plot(2)
    tree.plot(3)

if __name__ == "__main__":
    main()