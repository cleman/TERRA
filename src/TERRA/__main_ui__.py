from tree import Tree
from solver import Solver

from tkinter import *
from tkinter import messagebox
#from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from os import listdir

from Pages.genMapPage import generateMapPage
from Pages.genGridPage import generateGridPage
from Pages.genEdgesPage import generateEdgesPage
from Pages.solverPage import SolverPage
from Pages.otherPage import otherPage

from PIL import Image, ImageTk

mapPlot = None
def change_page(page):
    print(f"Changing page to {page.__class__.__name__}")
    page.tkraise()

def main():
    tree = Tree("map2")
    solver = None

    # Init window
    window = Tk()
    window.title("TERRA")
    window.geometry("1920x1080")
    window.minsize(960, 540)
    window["bg"] = "white"

    # Action Frame (left side of the window, 20% of the width)
    action_frame = Frame(window, bg="white", relief=GROOVE, borderwidth=2)
    action_frame.pack(side=LEFT, fill=Y)

    # View Frame (right side of the window, 80% of the width)
    view_frame = Frame(window, bg="white")
    view_frame.pack(side=RIGHT, fill=BOTH, expand=True)


    # Top bar frame for navigation buttons
    top_bar = Frame(action_frame, bg="white")
    top_bar.pack(side=TOP, fill=X)

    # Tools frame
    toolsFrame = Frame(action_frame, bg="white")
    toolsFrame.pack(fill=BOTH, expand=True)

    # Indicatives informations about the tree
    infoFrame = Frame(action_frame, relief=GROOVE, borderwidth=2)
    infoFrame.pack(side=BOTTOM, fill=X)

    buttonsize = 40
    img_name = ["map", "grid", "edges", "solver", "other"]
    img = [Image.open(f"data/logo/{name}.png") for name in img_name]
    img = [i.resize((buttonsize, buttonsize), Image.LANCZOS) for i in img]
    photo = [ImageTk.PhotoImage(i) for i in img]

    # Create page frames and add them to the mainFrame
    map_page = generateMapPage(tree, toolsFrame, window)
    grid_page = generateGridPage(tree, toolsFrame, window)
    edges_page = generateEdgesPage(tree, toolsFrame, window)
    solver_page = SolverPage(tree, toolsFrame, window)
    other_page = otherPage(tree, toolsFrame, window)

    toolsFrame.grid_rowconfigure(0, weight=1)
    toolsFrame.grid_columnconfigure(0, weight=1)

    for page in (map_page, grid_page, edges_page, solver_page, other_page):
        page.grid(row=0, column=0, sticky="nsew")

    Button(top_bar, image=photo[0], command=lambda: change_page(map_page)).pack(padx=10, pady=10, side=LEFT)
    Button(top_bar, image=photo[1], command=lambda: change_page(grid_page)).pack(padx=10, pady=10, side=LEFT)
    Button(top_bar, image=photo[2], command=lambda: change_page(edges_page)).pack(padx=10, pady=10, side=LEFT)
    Button(top_bar, image=photo[3], command=lambda: change_page(solver_page)).pack(padx=10, pady=10, side=LEFT)
    Button(top_bar, image=photo[4], command=lambda: change_page(other_page)).pack(padx=10, pady=10, side=LEFT)

    grid_page.tkraise()

    # Info frame content
    # Terminals
    num_terminals_label = Label(infoFrame, text="Number of terminals: 0", font=("Arial", 14))
    num_terminals_label.pack(padx=10, pady=5)
    # Candidaates
    num_candidates_label = Label(infoFrame, text="Number of points: 0", font=("Arial", 14))
    num_candidates_label.pack(padx=10, pady=5)
    # Edges
    num_edges_label = Label(infoFrame, text="Number of edges: 0", font=("Arial", 14))
    num_edges_label.pack(padx=10, pady=5)
    # Solution cost
    solution_cost_label = Label(infoFrame, text="Solution cost: N/A", font=("Arial", 14))
    solution_cost_label.pack(padx=10, pady=5)
    
    ########### View Frame ###########

    # Top bar frame
    view_top_bar = Frame(view_frame, bg="white", relief=GROOVE, borderwidth=2)
    view_top_bar.pack(side=TOP, fill=X)

    # Map view frame (square fixed size for the map view, 80% of the height)
    map_view_frame = Frame(view_frame, bg="white", )
    map_view_frame.pack(side=TOP, fill=BOTH, expand=True)


    ### Top bar of the view frame ###

    # Get available maps folder in /Maps
    maps_list = listdir("data/maps")
    maps_list.sort()

    # Map name entry and buttons
    map_name_label = Label(view_top_bar, text="Map Name:", font=("Arial", 14), bg="white")
    map_name_label.pack(padx=10, pady=10, side=LEFT)
    map_name_value = StringVar(value="map2")
    map_name_entry = ttk.Combobox(view_top_bar, width=20, font=("Arial", 14), textvariable=map_name_value, values=maps_list)
    map_name_entry.pack(padx=10, pady=10, side=LEFT)

    # Load map
    load_button = Button(view_top_bar, text="Load Map", font=("Arial", 14), command=lambda: [tree.__init__(map_name_value.get()), update_map_view()])
    load_button.pack(padx=10, pady=10, side=LEFT)

    def save_map():
        target_name = map_name_value.get()
        if not target_name:
            messagebox.showerror("Error", "Map name cannot be empty.")
            return

        if (tree.map.get_name() == target_name):
            tree.save_tree()
        else:
            response = messagebox.askyesno("Map name mismatch", "The loaded map name differs from the current name. Do you want to save the map with the current name?")

            if response:
                tree.set_name(target_name)
                tree.save_tree()
            else:
                messagebox.showinfo("Save Cancelled", "Map save operation cancelled.")
                return
    
    # Save map
    save_button = Button(view_top_bar, text="Save Map", font=("Arial", 14), command=lambda: save_map())
    save_button.pack(padx=10, pady=10, side=LEFT)

    # Radio buttons for map view options (Environment, Terminals, Candidates, Edges, Solution), could be multiple selection, default value is Environment and Terminals
    view_options = ["Environment", "Terminals", "Candidates", "Edges", "Solution"]
    view_options_var = [StringVar(value=option) for option in view_options]
    view_options_values = [BooleanVar(value=True) for _ in view_options[:2]] + [BooleanVar(value=False) for _ in view_options[2:]]
    for i, option in enumerate(view_options):
        Checkbutton(view_top_bar, text=option, variable=view_options_values[i], onvalue=True, offvalue=False, font=("Arial", 14), bg="white", command=lambda: update_map_view()).pack(padx=10, pady=10, side=LEFT)

    # Variable page to raise
    page_to_raise_int = IntVar(value=1)

    # Exit button at the end of the top bar
    exit_button = Button(view_top_bar, text="Exit", font=("Arial", 14), command=window.quit)
    exit_button.pack(padx=10, pady=10, side=RIGHT)

    def update_map_view():
        global mapPlot
        # Close previous plot
        plt.close()
        if mapPlot is not None:
            mapPlot.get_tk_widget().destroy()
        

        bool_values = [var.get() for var in view_options_values]

        #print("Updating map view with options:")
        #for option, var in zip(view_options, view_options_values):
        #    print(f"  {option}: {var.get()}")
        
        if mapPlot is not None:
            mapPlot.get_tk_widget().destroy()
        
        tree.plot(bool_values)
        mapPlot = FigureCanvasTkAgg(tree.map.fig, master=map_view_frame)        # fixed square size for the map view
        mapPlot.get_tk_widget().pack()

        # Raise the correct page
        switch_page = {0: map_page, 1: grid_page, 2: edges_page, 3: solver_page, 4: other_page}
        switch_page[page_to_raise_int.get()].tkraise()

        # Update the info frame labels
        num_terminals_label.config(text=f"Number of terminals: {tree.get_nb_terminals()}")
        num_candidates_label.config(text=f"Number of candidates: {len(tree.get_candidates())}")
        num_edges_label.config(text=f"Number of edges: {len([a for a in tree.get_edges() if a[2] < 1e10])}")
        if tree.get_solution_cost() is not None:
            solution_cost_label.config(text=f"Solution cost: {tree.get_solution_cost()}")
        else:
            solution_cost_label.config(text="Solution cost: N/A")
        
    # Generate map page
    map_page.mapdata_var = view_options_values
    map_page.terminals_var = view_options_values
    map_page.raise_page_var = page_to_raise_int
    map_page.refresh_callback = update_map_view
    
    # Grid page
    grid_page.candidates_var = view_options_values
    grid_page.raise_page_var = page_to_raise_int
    grid_page.refresh_callback = update_map_view

    # Edges page
    edges_page.candidates_edges_var = view_options_values
    edges_page.raise_page_var = page_to_raise_int
    edges_page.refresh_callback = update_map_view

    # Solver
    solver_page.solver_var = view_options_values
    solver_page.raise_page_var = page_to_raise_int
    solver_page.refresh_callback = update_map_view

    # Other
    other_page.other_var = view_options_values
    other_page.raise_page_var = page_to_raise_int
    other_page.refresh_callback = update_map_view

    # Update the map view
    update_map_view()

    window.mainloop()

    return True


if __name__ == "__main__":
    main()