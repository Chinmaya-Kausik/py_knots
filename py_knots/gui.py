import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.mathtext import math_to_image
from io import BytesIO
from PIL import ImageTk, Image
from sympy import latex

from sgraph import *
from braid import *
from col_perm import *
from pres_mat import *
from visualization import *
from typing import List, Tuple, Callable, Dict


font_style = "Calibri"
font_size = 25


class Clasper(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # Configure messages for defaults
        self.default_strands = tk.Frame(self)
        self.default_strands.grid(
            column=0, row=4, pady=10, sticky='W')
        self.default_colours = tk.Frame(self)
        self.default_colours.grid(
            column=1, row=4, pady=10, sticky='W')
        self.default_orient = tk.Frame(self)
        self.default_orient.grid(
            column=2, row=4, pady=10, sticky='W')
        self.default_signature = tk.Frame(self)
        self.default_signature.grid(
            column=3, row=4, pady=10, sticky='W')

        """----- Implementing the GUI ---- """

        # Instructions for entering braids
        ttk.Label(
            self, text='''Braids - LinkInfo or comma/space separated.'''+
            '''\nColours and signature inputs - space separated.'''
            '''\nBFD = leave blank for default''',
            font=(font_style, font_size), background='yellow').grid(
            column=0, row=0, columnspan=4)

        # Setting up the entry for the braid
        ttk.Label(
            self, text='Braid:', font=(font_style, font_size)).grid(
            column=0, row=1, pady=10)
        self.braid_str = tk.StringVar()
        ttk.Entry(self, textvariable=self.braid_str,
            font=(font_style, font_size), width=40).grid(column=1, row=1,
            padx=0, pady=10, sticky='W', columnspan=3)

        # Setting up the entry for strands
        ttk.Label(
            self, text='Number of Strands (BFD):',
            font=(font_style, font_size)).grid(column=0, row=2, pady=10)
        self.strand_str = tk.StringVar()
        ttk.Entry(self, textvariable=self.strand_str,
            font=(font_style, font_size)).grid(
            column=1, row=2, padx=0, pady=10, sticky='W', columnspan=3)

        # Creating a style object
        style = ttk.Style()
         
        # Adding style for buttons
        style.configure('C.TButton', font=('calibri', font_size),
            background='blue')

        # Setup for printing the cycle decomposition
        ttk.Button(self, text="Cycle Decomposition", command=self.compute_cyc,
            style='C.TButton').grid(column=0, row=3, pady=10)

        # Set up entry for the colour list
        ttk.Label(self, text='Colours (start from 0, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=5, pady=10)
        self.colour_list = tk.StringVar()
        ttk.Entry(self, textvariable=self.colour_list,
            font=(font_style, font_size)).grid(
            column=1, row=5, padx=0, pady=10, sticky='W', columnspan=3)

        # Set up entry for orientations of colours
        ttk.Label(self, text='Orientations (+1/-1, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=6, pady=10)
        self.colour_signs = tk.StringVar()
        ttk.Entry(self, textvariable=self.colour_signs,
            font=(font_style, font_size)).grid(
            column=1, row=6, padx=0, pady=10, sticky='W', columnspan=3)

        # Set up entry for complex tuple
        ttk.Label(self, text='Signature input,'+
            'space sep\n (1/3 means 2*pi/3, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=7, pady=10)
        self.cplx_tuple = tk.StringVar()
        ttk.Entry(self, textvariable=self.cplx_tuple,
            font=(font_style, font_size)).grid(
            column=1, row=7, padx=0, pady=10, sticky='W', columnspan=2)

        self.invariant_frame = tk.Frame(self)

        # Button to compute invariants
        ttk.Button(self, text="Compute Invariants",
        command=self.get_invariants, style='C.TButton').grid(
            column=0, row=8, pady=10)

        # Button to view the braid
        ttk.Button(self, text="View Braid",
        command=self.view_braid, style='C.TButton').grid(
            column=1, row=8, pady=10)

        # Button to view the C-Complex
        ttk.Button(self, text="View C-Complex",
        command=self.view_c_complex, style='C.TButton').grid(
            column=2, row=8, pady=10)

    # Processing Link Info style inputs
    def link_info(self, braid: str) -> Braid:
        self.default_strands.destroy()
        self.default_strands = tk.Frame(self)
        self.default_strands.grid(
            column=0, row=4, pady=10)

        Message = ""
        try:
            start = braid.index('{')+1
            strands = int(braid[start])
            new_braid = braid[start:]
            braid1 = new_braid[
                new_braid.index('{')+1: new_braid.index('}')].split(',')
            braid1 = list(map(lambda x: int(x), braid1))
        except ValueError:
            Message += "Invalid Link Info input. "
            braid1 = []
            strands = 0

        ttk.Label(self.default_strands, text=str(Message),
            font=(font_style, font_size)).pack()

        return Braid(braid1, strands)

    # Processing comma separated inputs
    def csv_input(self, braid: str, strands: str) -> Braid:
        self.default_strands.destroy()
        self.default_strands = tk.Frame(self)
        self.default_strands.grid(
            column=0, row=4, pady=10)

        Message = ""
        try:
            braid1 = [int(x) for x in braid.strip().split(" ")]
        except ValueError:
            Message += "Invalid braid input. "
            braid1 = []
            strands = 0

        try:
            strands = int(strands)
        except ValueError:
            Message += "Using default strands. "
            strands = max(list(map(lambda x: abs(x), braid1)))+1

        ttk.Label(self.default_strands, text=str(Message),
            font=(font_style, font_size)).pack()

        return Braid(braid1, strands)

    # Processing space separated inputs
    def space_input(self, braid: str, strands: str) -> Braid:
        self.default_strands.destroy()
        self.default_strands = tk.Frame(self)
        self.default_strands.grid(
            column=0, row=4, pady=10)

        Message = ""
        try:
            braid1 = [int(x) for x in braid.strip().split(" ")]
        except ValueError:
            Message += "Invalid braid input. "
            braid1 = []
            strands = 0

        try:
            strands = int(strands)
        except ValueError:
            Message += "Using default strands. "
            strands = max(list(map(lambda x: abs(x), braid1)))+1
        
        ttk.Label(self.default_strands, text=str(Message),
            font=(font_style, font_size)).pack()

        return Braid(braid1, strands)

    # Command for computing the cycle decomposition and generating the braid
    def compute_cyc(self) -> Braid:
        # Obtain the braid and strands and process them
        braid = self.braid_str.get()
        strands = self.strand_str.get()

        # Try all possible input formats
        if('{' in braid):
            p = self.link_info(braid)
        elif(',' in braid):
            p = self.csv_input(braid, strands)
        else:
            p = self.space_input(braid, strands)

        ttk.Label(self, text=str(p.cycle_decomp),
            font=(font_style, font_size)).grid(
            column=1, row=3, pady=10, sticky='W')

        return p

    # Command for getting the coloured braid
    def get_col_braid(self) -> ColBraid:
        self.default_colours.destroy()
        self.default_orient.destroy()

        self.default_colours = tk.Frame(self)
        self.default_colours.grid(
            column=1, row=4, pady=10, sticky='W')

        self.default_orient = tk.Frame(self)
        self.default_orient.grid(
            column=2, row=4, pady=10, sticky='W')

        p = self.compute_cyc()
        col_list = self.colour_list.get()
        col_signs = self.colour_signs.get()

        try:
            col_list = [int(x) for x in col_list.split(" ")]
        except ValueError:
            ttk.Label(self.default_colours, text="Default colors.",
                font=(font_style, font_size)).pack()
            col_list = list(range(p.ct_knots))

        p = ColBraid(p.braid, p.strands, col_list)

        try:
            col_signs = [int(x) for x in col_signs.split(" ")]
        except ValueError:
            ttk.Label(self.default_orient, text="Default orientations.",
                font=(font_style, font_size)).pack()
            col_signs = [1]*(p.ct_knots)

        p, col_signs = find_min_perm(p, col_signs, 50)

        return p

    # Command for generating the spline graph;
    def get_graph(self) -> SGraph:
        self.default_colours.destroy()
        self.default_orient.destroy()

        self.default_colours = tk.Frame(self)
        self.default_colours.grid(
            column=1, row=4, pady=10, sticky='W')

        self.default_orient = tk.Frame(self)
        self.default_orient.grid(
            column=2, row=4, pady=10, sticky='W')

        p = self.compute_cyc()
        col_list = self.colour_list.get()
        col_signs = self.colour_signs.get()

        try:
            col_list = [int(x) for x in col_list.split(" ")]
        except ValueError:
            ttk.Label(self.default_colours, text="Default colors.",
                font=(font_style, font_size)).pack()
            col_list = list(range(p.ct_knots))

        p = ColBraid(p.braid, p.strands, col_list)

        try:
            col_signs = [int(x) for x in col_signs.split(" ")]
        except ValueError:
            ttk.Label(self.default_orient, text="Default orientations.",
                font=(font_style, font_size)).pack()
            col_signs = [1]*(p.ct_knots)

        p, col_signs = find_min_perm(p, col_signs, 50)
        graph = p.make_graph(col_signs)
        return graph

    # Command for computing and displaying invariants
    def get_invariants(self):

        self.invariant_frame.destroy()
        self.invariant_frame = Inv(self)
        self.invariant_frame.grid(column=0, row=9,
            columnspan=4, rowspan=3, sticky='W')

    # Command to view the braid
    def view_braid(self):
        fig = visualize_braid(self.get_col_braid())

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
      
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().grid(column=0, row=12, columnspan=4)

    # Command to view the C-Complex
    def view_c_complex(self):

        fig = visualize_clasp_complex(self.get_graph())

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
      
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().grid(column=0, row=13, columnspan=4)

# Class for invariants
class Inv(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        parent.default_signature.destroy()
        parent.default_signature = tk.Frame(parent)
        parent.default_signature.grid(
            column=3, row=4, pady=10, sticky='W')

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        try:
            graph = parent.get_graph()
        except ValueError:
            pass

        try:
            complex_tuple = [int(x) for x in 
                parent.cplx_tuple.get().split(" ")]
            omega = [complex(cos(2*pi*x), sin(2*pi*x))
                for x in complex_tuple]
        except ValueError:
            omega = [complex(-1, 0)]*len(graph.col_signs)
            ttk.Label(parent.default_signature,
                text="Default signature inputs.",
                font=(font_style, font_size)).pack()

        pm = presentation_matrix(graph)

        ttk.Label(self, text='Conway Potential Function:',
            font=(font_style, font_size)).grid(
            column=0, row=0, pady=10)

        self.make_latex_label(latex(pm.conway_potential_function(graph)),
            column=1, row=0, y_pad=10, sticky='W',
            columnspan=3, rowspan=1, size=(2000, 100))

        ttk.Label(self, text='Multivariable Alexander Polynomial:',
            font=(font_style, font_size)).grid(
            column=0, row=1, pady=10)

        self.make_latex_label(latex(pm.multivar_alexander_poly(graph)),
            column=1, row=1, y_pad=10, sticky='W',
            columnspan=3, rowspan=1, size=(2000, 50))

        ttk.Label(self, text='Signature:',
            font=(font_style, font_size)).grid(
            column=0, row=2, pady=15)

        ttk.Label(self, text=str(pm.signature(omega)),
            font=(font_style, 30)).grid(
            column=1, row=2, pady=15, sticky='W')

    # Renders latex as a label and places it on the grid
    def make_latex_label(self, latex_string: str, column: int,
            row: int, y_pad: int, sticky: str, columnspan: int, rowspan: int,
            size = Tuple[int, int]):

        # Creating buffer for storing image in memory
        buffer = BytesIO()

        # Writing png image with our rendered latex text to buffer
        math_to_image("$" + latex_string + "$",
            buffer, dpi=1000, format='png')

        # Remoting buffer to 0, so that we can read from it
        buffer.seek(0)

        # Creating Pillow image object from it
        pimage= Image.open(buffer)
        pimage.thumbnail(size)

        # Creating PhotoImage object from Pillow image object
        image = ImageTk.PhotoImage(pimage)

        # Creating label with our image
        label = ttk.Label(self, image=image)

        # Storing reference to our image object so it's not garbage collected,
        # since TkInter doesn't store references by itself
        label.img = image

        label.grid(column=column, row=row, pady=y_pad, sticky=sticky,
            columnspan=columnspan, rowspan=rowspan)

        buffer.flush()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Clasper")

    window_width = 2400
    window_height = 2400

    # Get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Find the center point
    center_x = int(screen_width/2)
    center_y = int(screen_height/2)

    # Set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{0}')

    clasper = Clasper(root)
    clasper.pack(side="top", fill="both", expand=True)

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()
