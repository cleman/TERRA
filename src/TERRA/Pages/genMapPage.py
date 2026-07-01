import tkinter as tk
from tkinter import ttk


class generateMapPage(tk.Frame):
    def __init__(self, tree, parent, controller):

        self.tree = tree
        self.refresh_callback = None
        self.mapdata_var = None
        self.terminals_var = None
        self.raise_page_var = None

        # region global elements
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Generate Map", font=("Arial", 24))
        label.pack(pady=10, padx=10)

        # Frame for map data
        mapData_Frame = tk.Frame(self, borderwidth=2, relief="groove")
        mapData_Frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        # Frame for terminals
        terminals_Frame = tk.Frame(self, borderwidth=2, relief="groove")
        terminals_Frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        # Labels
        tk.Label(mapData_Frame, text="Map Data", font=("Arial", 14)).pack(padx=5, pady=5)
        tk.Label(terminals_Frame, text="Terminals", font=("Arial", 14)).pack(padx=5, pady=5)
        # endregion


        ################### Map Data ###################

        # region Map data frames
        mapData_Top_Frame = tk.Frame(mapData_Frame)
        mapData_Top_Frame.pack(side=tk.TOP, fill="x", padx=5, pady=5)

        mapData_Labels_Frame = tk.Frame(mapData_Top_Frame)
        mapData_Labels_Frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        mapData_SpinBoxes_Frame = tk.Frame(mapData_Top_Frame)
        mapData_SpinBoxes_Frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        mapData_Buttons_Frame = tk.Frame(mapData_Frame)
        mapData_Buttons_Frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # endregion

        # region List of map data labels
        mapData_MapSize_Label = tk.Label(mapData_Labels_Frame, text="Map Size", font=("Arial", 14))
        mapData_NbObstacles_Label = tk.Label(mapData_Labels_Frame, text="Number of Obstacles", font=("Arial", 14))
        mapData_SizeObstacles_Label = tk.Label(mapData_Labels_Frame, text="Size of Obstacles", font=("Arial", 14))
        # endregion

        # region mapdata spin boxes
        mapData_MapSize_Value = tk.StringVar(value="100")
        mapData_MapSize_Spinbox = tk.Spinbox(mapData_SpinBoxes_Frame, from_=0, to=10000, width=10, textvariable=mapData_MapSize_Value, font=("Arial", 14))

        mapData_NbObstacles_Value = tk.StringVar(value="10")
        mapData_NbObstacles_Spinbox = tk.Spinbox(mapData_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=mapData_NbObstacles_Value, font=("Arial", 14))

        mapData_SizeObstacles_Value = tk.StringVar(value="20")
        mapData_SizeObstacles_Spinbox = tk.Spinbox(mapData_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=mapData_SizeObstacles_Value, font=("Arial", 14))
        # endregion

        # regionButtons for map data
        mapData_Generate_Button = tk.Button(mapData_Buttons_Frame, text="Generate", font=("Arial", 14), command=lambda: self.generate_map(
            mapData_MapSize_Value.get(), 
            mapData_NbObstacles_Value.get(), 
            mapData_SizeObstacles_Value.get()
        ))
        #mapData_Save_Button = tk.Button(mapData_Buttons_Frame, text="Save", font=("Arial", 14))#, command=lambda: self.save_map(mapData_MapSize_Value.get(), mapData_NbObstacles_Value.get(), mapData_SizeObstacles_Value.get()))
        #mapData_Load_Button = tk.Button(mapData_Buttons_Frame, text="Load", font=("Arial", 14))#, command=lambda: self.load_map(mapData_MapSize_Value.get(), mapData_NbObstacles_Value.get(), mapData_SizeObstacles_Value.get()))
        # endregion

        # region Pack map data labels and spin boxes
        pad_valx = 1
        pad_valy = 0
        mapData_MapSize_Label.pack(padx=pad_valx, pady=pad_valy)
        mapData_MapSize_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        mapData_NbObstacles_Label.pack(padx=pad_valx, pady=pad_valy)
        mapData_NbObstacles_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        mapData_SizeObstacles_Label.pack(padx=pad_valx, pady=pad_valy)
        mapData_SizeObstacles_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        mapData_Generate_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        #mapData_Save_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        #mapData_Load_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        # endregion


        ################### Terminals and root ###################

        # region terminals frames
        terminals_Top_Frame = tk.Frame(terminals_Frame)
        terminals_Top_Frame.pack(side=tk.TOP, fill="x", padx=5, pady=5)

        terminals_Labels_Frame = tk.Frame(terminals_Top_Frame)
        terminals_Labels_Frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        terminals_SpinBoxes_Frame = tk.Frame(terminals_Top_Frame)
        terminals_SpinBoxes_Frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        terminals_Buttons_Frame = tk.Frame(terminals_Frame)
        terminals_Buttons_Frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # endregion

        # region terminals labels
        terminals_NbTerminals_Label = tk.Label(terminals_Labels_Frame, text="Number of Terminals", font=("Arial", 14))
        terminals_DistTerminals_Label = tk.Label(terminals_Labels_Frame, text="Distance between Terminals", font=("Arial", 14))
        terminals_DistCenter_Label = tk.Label(terminals_Labels_Frame, text="Distance from Center", font=("Arial", 14))
        terminals_DistObstacles_Label = tk.Label(terminals_Labels_Frame, text="Distance from Obstacles", font=("Arial", 14))
        # endregion

        # region terminals spin boxes
        # Lst of spin boxes for map data
        terminals_NbTerminals_Value = tk.StringVar(value="6")
        terminals_NbTerminals_Spinbox = tk.Spinbox(terminals_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=terminals_NbTerminals_Value, font=("Arial", 14))

        terminals_DistTerminals_Value = tk.StringVar(value="5")
        terminals_DistTerminals_Spinbox = tk.Spinbox(terminals_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=terminals_DistTerminals_Value, font=("Arial", 14))

        terminals_DistCenter_Value = tk.StringVar(value="20")
        terminals_DistCenter_Spinbox = tk.Spinbox(terminals_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=terminals_DistCenter_Value, font=("Arial", 14))

        terminals_DistObstacles_Value = tk.StringVar(value="5")
        terminals_DistObstacles_Spinbox = tk.Spinbox(terminals_SpinBoxes_Frame, from_=0, to=100, width=10, textvariable=terminals_DistObstacles_Value, font=("Arial", 14))
        # endregion

        # Buttons for map data
        terminals_Generate_Button = tk.Button(terminals_Buttons_Frame, text="Generate", font=("Arial", 14), command=lambda: self.generate_terminals(
            terminals_NbTerminals_Value.get(),
            terminals_DistTerminals_Value.get(),
            terminals_DistCenter_Value.get(),
            terminals_DistObstacles_Value.get()
        ))
        #terminals_Save_Button = tk.Button(terminals_Buttons_Frame, text="Save", font=("Arial", 14))#, command=lambda: self.save_map(terminals_MapSize_Value.get(), terminals_NbObstacles_Value.get(), terminals_SizeObstacles_Value.get()))
        #terminals_Load_Button = tk.Button(terminals_Buttons_Frame, text="Load", font=("Arial", 14))#, command=lambda: self.load_map(terminals_MapSize_Value.get(), terminals_NbObstacles_Value.get(), terminals_SizeObstacles_Value.get()))
        # endregion

        # region Pack terminals labels and spin boxes
        pad_valx = 1
        pad_valy = 0
        terminals_NbTerminals_Label.pack(padx=pad_valx, pady=pad_valy)
        terminals_NbTerminals_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistTerminals_Label.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistTerminals_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistCenter_Label.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistCenter_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistObstacles_Label.pack(padx=pad_valx, pady=pad_valy)
        terminals_DistObstacles_Spinbox.pack(padx=pad_valx, pady=pad_valy)
        terminals_Generate_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        #terminals_Save_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        #terminals_Load_Button.pack(fill="x", padx=pad_valx, pady=pad_valy)
        # endregion

    
    def generate_map(self, map_size, nb_obstacles, size_obstacles):
        print(f"Generating map with size {map_size}, {nb_obstacles} obstacles of size {size_obstacles}")
        # Call the tree method to generate the map
        self.tree.generate_map(int(map_size), int(nb_obstacles), int(size_obstacles))
        print(f"Number of obstacles: {len(self.tree.get_obstacles())}")

        view_configuration = [True, False, False, False, False]

        # If the edges view is not enabled, enable it
        if self.mapdata_var is not None:
            for i in range (len(view_configuration)):
                self.mapdata_var[i].set(view_configuration[i])
        self.raise_page_var.set(0)

        # Refresh the map view to show the new edges
        if callable(self.refresh_callback):
            self.refresh_callback()
    
    def generate_terminals(self, nb_terminals, dist_terminals, dist_center, dist_obstacles):
        print(f"Generating {nb_terminals} terminals with distance {dist_terminals}, center distance {dist_center}, and obstacle distance {dist_obstacles}")
        # Call the tree method to generate the terminals
        self.tree.generate_terminals(int(nb_terminals), int(dist_terminals), int(dist_center), int(dist_obstacles))
        print(f"Number of terminals: {self.tree.get_nb_terminals()}")

        view_configuration = [True, True, False, False, False]

        # If the terminals view is not enabled, enable it
        if self.terminals_var is not None:
            for i in range (len(view_configuration)):
                self.terminals_var[i].set(view_configuration[i])
        self.raise_page_var.set(0)

        # Refresh the map view to show the new terminals
        if callable(self.refresh_callback):
            self.refresh_callback()