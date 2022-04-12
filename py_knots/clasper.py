import tkinter as tk
from tkinter import ttk
from matplotlib.pyplot import close
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.mathtext import math_to_image
from io import BytesIO
from PIL import ImageTk, Image
from sympy import latex
from math import pi, cos, sin
from sgraph import *
from braid import *
from col_perm import *
from pres_mat import *
from visualization import *
from casson_gordon import *
from typing import List, Tuple, Callable, Dict


font_style = "Calibri"
font_size = 25


# Class for main window
class Clasper(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # Configure variables
        self.braid_str = tk.StringVar()
        self.complete_graph = tk.IntVar(value=0)

        # Configure frames for checking the braid
        self.braid_check = tk.Frame(self)
        self.cycle_decomp_frame = tk.Frame(self)
        self.euler_char_frame = tk.Frame(self)
        self.euler_char_frame.grid(column=2, row=3, pady=10, sticky='W')
        self.euler_char_frame.grid_columnconfigure(0, weight=3)
        self.euler_char_frame.grid_columnconfigure(0, weight=1)
        self.euler_char_frame.euler_char_val = tk.Frame(self.euler_char_frame)

        # Configure frames for everything
        self.strands = Strands(self)
        self.strands.grid(
            column=0, row=4, pady=10, rowspan=6, sticky='N')
        self.color = Color(self)
        self.color.grid(
            column=1, row=4, pady=10, rowspan=6, sticky='N')
        self.signature = Signature(self)
        self.signature.grid(
            column=2, row=4, pady=10, rowspan=6, sticky='N')

        self.braid_visual = tk.Frame(self)
        self.braid_visual.grid(
            column=0, row=14, pady=10, columnspan=4, sticky='N')
        self.ccomplex_visual = tk.Frame(self)
        self.ccomplex_visual.grid(
            column=0, row=15, pady=10, columnspan=4, sticky='N')

        self.invariant_frame = tk.Frame(self)
        self.invariant_frame.grid(column=0, row=11,
            columnspan=4, rowspan=3)

        """


        ----- Implementing the GUI ----


        
        """

        # (0, 0) Instructions for entering braids
        ttk.Label(
            self, text='''Braids - LinkInfo format or comma/space '''+
            '''separated. Colors and signature inputs - space separated.\n'''+
            '''Press enter to compute invariants with defaults.'''
            ''' See paper for details about the C-Complex.\n'''+
            '''Written by Chinmaya Kausik.''',
            font=(font_style, font_size), background='cyan').grid(
            column=0, row=0, columnspan=4)

        # (0, 0->1) Setting up the entry for the braid
        ttk.Label(
            self, text='Braid:', font=(font_style, font_size)).grid(
            column=0, row=1, pady=10)
        ttk.Entry(self, textvariable=self.braid_str,
            font=(font_style, font_size), width=40).grid(column=1, row=1,
            padx=0, pady=10, sticky='W', columnspan=2)

        # (1, 2) Examples for braid entries
        ttk.Label(
            self, text="""Example: '-2 -3 2 -3 -1 -2 -3'"""+
            """ or '-2, -3, 2, -3, -1, -2, -3' or """+
            """'{4, {-2, -3, 2, -3, -1, -2, -3}}'""",
            font=(font_style, font_size), background='cyan').grid(
            column=1, row=2, pady=10, sticky='W', columnspan=3)

        # Creating a style object
        style = ttk.Style()

        # Adding style for buttons
        style.configure('C.TButton', font=('calibri', font_size),
            background='blue')

        # Adding style for radiobuttons
        style.configure('C.TRadiobutton', font=('calibri', font_size))

        # Adding style for checkbuttons
        style.configure('C.TCheckbutton', font=('calibri', font_size))

        ttk.Checkbutton(self, text="All Seifert surfaces intersecting",
            style='C.TCheckbutton',
            variable=self.complete_graph).grid(column=2, row=1,
            padx=30, pady=10, sticky='W')
        
        # Setup for printing the cycle decomposition
        ttk.Button(self, text="Cycle Decomposition", command=self.compute_cyc,
            style='C.TButton').grid(column=0, row=3, pady=10)

        # Setup for printing the Euler Characteristic of the C-Complex
        ttk.Button(self.euler_char_frame, text="Euler Characteristic of C-Complex",
            command=self.get_sgraph_euler_char,
            style='C.TButton').grid(column=0, row=0, pady=10, sticky='W')

        # Button to compute invariants
        ttk.Button(self, text="Compute link invariants",
        command=self.get_invariants, style='C.TButton').grid(
            column=0, row=10, pady=10)

        ttk.Button(self, text="Invariants in LaTeX",
            command=self.get_latex, style='C.TButton').grid(
            column=1, row=10, pady=10)

        ttk.Button(self, text="Export Seifert matrices",
            command=self.get_seifert_matrices, style='C.TButton').grid(
            column=2, row=10, pady=10)

    # Compute invariants with defaults
    def compute_with_defaults(self, int: int):
        self.strands.strand_choice.set(1)
        self.color.color_choice.set(2)
        self.signature.signature_choice.set(1)
        self.get_invariants()

    # Processing Link Info style inputs
    def link_info(self, braid: str) -> Braid:

        start = braid.index('{')+1
        strands = int(braid[start])
        new_braid = braid[start:]
        braid1 = new_braid[
            new_braid.index('{')+1: new_braid.index('}')].split(',')
        braid1 = list(filter(lambda x: x.strip()!="", braid1))
        braid1 = list(map(lambda x: int(x), braid1))

        return Braid(braid1, strands)

    # Processing comma separated inputs
    def csv_input(self, braid: str) -> List[int]:
        braid1 = braid.strip().split(",")
        braid1 = list(filter(lambda x: x.strip()!="", braid1))
        braid1 = [int(x) for x in braid1]
        return braid1

    # Processing space separated inputs
    def space_input(self, braid: str) -> List[int]:
        braid1 = braid.strip().split(" ")
        braid1 = list(filter(lambda x: x.strip()!="", braid1))
        braid1 = [int(x) for x in braid1]
        return braid1

    # Command for computing the cycle decomposition and generating the braid
    def compute_cyc(self) -> Braid:
        self.cycle_decomp_frame.destroy()
        self.cycle_decomp_frame = tk.Frame(self)
        self.cycle_decomp_frame.grid(
            column=1, row=3, pady=10, sticky='W')
        p_braid = self.strands.make_braid()
        ttk.Label(self.cycle_decomp_frame, text=str(p_braid.cycle_decomp),
            font=(font_style, font_size)).pack()

    # Command for computing the cycle decomposition and generating the braid
    def get_sgraph_euler_char(self) -> Braid:
        self.euler_char_frame.euler_char_val.destroy()
        self.euler_char_frame.euler_char_val = tk.Frame(self.euler_char_frame)
        self.euler_char_frame.euler_char_val.grid(
            column=1, row=0, padx=20, pady=10, sticky='E')
        try:
            graph = self.color.get_graph()
            ttk.Label(self.euler_char_frame.euler_char_val,
                text="= "+str(graph.sgraph_euler_char()),
                font=(font_style, font_size)).pack()
        except Exception:
            pass

    # Print latex 
    def get_latex(self):
        new_window = tk.Toplevel(self)
        try:
            graph = self.color.get_graph()
            pm = presentation_matrix(graph)
            cpf = tk.Text(new_window, font=(font_style, font_size))
            cpf.insert(1.0, "Conway Potential Function:\n"+
                latex(pm.conway_potential_function(graph)))
            cpf.pack()
            cpf.configure(state="disabled")

            multi_var_alexander = tk.Text(
                new_window, font=(font_style, font_size))
            multi_var_alexander.insert(1.0,
                "Mutivariable Alexander Polynomial:\n"+
                latex(pm.conway_potential_function(graph)))
            multi_var_alexander.pack()
            multi_var_alexander.configure(state="disabled")

            # if tkinter is 8.5 or above you'll want the selection background
            # to appear like it does when the widget is activated
            # comment this out for older versions of Tkinter
            cpf.configure(inactiveselectbackground=cpf.cget(
                "selectbackground"))
            multi_var_alexander.configure(
                inactiveselectbackground=cpf.cget("selectbackground"))
            
        except ValueError:
            pass

    # Save the seifert matrices to a file
    def get_seifert_matrices(self):
        file_name = tk.filedialog.asksaveasfilename()

        self.invariant_frame.destroy()
        self.invariant_frame = Inv(self)
        self.invariant_frame.grid(column=0, row=11,
            columnspan=4, rowspan=3)

        p = self.strands.make_braid()
        graph = self.invariant_frame.graph

        if(file_name):
            if("." not in file_name):
                file_name += ".txt"

            f = open(file_name, 'w+')
            seif = create_seifert_matrices(graph)
            f.write("Braid: "+str(p.braid_wrong))
            f.write("\nStrands: "+str(p.strands)+"\n\n")
            f.write(seif)
            f.close()

    # Command for computing and displaying invariants
    def get_invariants(self):

        self.invariant_frame.destroy()
        self.invariant_frame = Inv(self)
        self.invariant_frame.grid(column=0, row=11,
            columnspan=4, rowspan=3)
        self.view_braid()
        self.view_c_complex()

    # Command to view the braid
    def view_braid(self):
        try:
            close(self.braid_fig)
        except Exception:
            pass
        self.braid_visual.destroy()
        self.braid_visual = tk.Frame(self)
        self.braid_visual.grid(
            column=0, row=14, pady=10, columnspan=4)

        self.braid_fig = visualize_braid(self.color.get_col_braid())

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(self.braid_fig, master=self.braid_visual)
        canvas.draw()
      
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack()

    # Command to view the C-Complex
    def view_c_complex(self):
        try:
            close(self.ccomplex_fig)
        except Exception:
            pass
        self.ccomplex_visual.destroy()
        self.ccomplex_visual = tk.Frame(self)
        self.ccomplex_visual.grid(
            column=0, row=15, pady=10, columnspan=4)

        self.ccomplex_fig = visualize_clasp_complex(self.color.get_graph())

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(self.ccomplex_fig,
            master=self.ccomplex_visual)
        canvas.draw()
      
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack()


# Class for invariants
class Inv(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        try:
            graph = parent.color.get_graph()
            self.graph = graph
        except ValueError:
            pass

        omega = parent.signature.get_omega()

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

        ttk.Label(self, text='Cimasoni-Florens Signature:',
            font=(font_style, font_size)).grid(
            column=0, row=2, pady=15)

        signat = pm.signature(omega)

        ttk.Label(self, text=str(signat[0]), font=(font_style, 30)).grid(
            column=1, row=2, pady=15, sticky='W')

        eig_val = "(Eigenvalues: {})".format(list(signat[1]))
        ttk.Label(self, text=str(eig_val), font=(font_style, 25)).grid(
            column=2, row=2, columnspan=2, padx=10, pady=15, sticky='W')

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


# Class for strand inputs
class Strands(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        braid = self.parent.braid_str.get()

        # Configure the two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Add title
        ttk.Label(
            self, text='''Number of strands''',
            font=(font_style, font_size), background='yellow').grid(
            column=0, row=0, columnspan=2)

        # Configure frame for printing defaults
        self.strand_default = tk.Frame(self)
        self.strand_check = tk.Frame(self)

        # Configure variables to hold inputs
        self.strand_choice = tk.IntVar(value=0)
        self.strand_str = tk.StringVar()

        # Configure and place radio buttons and entries
        # Default
        self.use_defaults = ttk.Radiobutton(self, text="Default",
            variable=self.strand_choice,
            style='C.TRadiobutton', value=1, command=self.make_braid)
        self.use_defaults.grid(column=0, row=1, pady=10, sticky='W')
        # Custom
        self.use_custom = ttk.Radiobutton(self, text="Custom: ",
            variable=self.strand_choice,
            style='C.TRadiobutton', value=2, command=self.make_braid)
        self.use_custom.grid(column=0, row=2, pady=10, sticky='W')
        ttk.Entry(self, textvariable=self.strand_str,
            font=(font_style, font_size)).grid(
            column=1, row=2, padx=0, pady=10, sticky='W')
        # Example of a custom entry
        ttk.Label(self, text="Example: '3'",
            font=(font_style, font_size), background='cyan').grid(
            column=1, row=3, pady=10, sticky='W')

    # Make a braid and return error messages
    def make_braid(self) -> Braid:
        # Destroy and reinitialize message frames
        self.parent.braid_check.destroy()
        self.strand_default.destroy()
        self.strand_check.destroy()
        self.strand_check = tk.Frame(self)
        self.strand_default = tk.Frame(self)
        self.parent.braid_check = tk.Frame(self.parent)

        self.parent.braid_check.grid(column=0, row=2, pady=10)
        self.strand_default.grid(column=1, row=1, pady=10, sticky='W')
        self.strand_check.grid(column=0, row=5, pady=10, columnspan=2)

        strand_check_message = ""
        braid = self.parent.braid_str.get()

        try:
            strand_option = self.strand_choice.get()
            assert strand_option != 0, AssertionError

            if('{' in braid):
                p = self.parent.link_info(braid)
            elif(',' in braid):
                braid1 = self.parent.csv_input(braid)
            else:
                braid1 = self.parent.space_input(braid)
        except AssertionError:
            strand_check_message += "Specify strands."
        except ValueError:
            ttk.Label(self.parent.braid_check, text="Bad braid input",
                font=(font_style, font_size), background="pink").pack()

        try:
            if(strand_option == 2):
                strands = self.strand_str.get()
                strands = int(strands)
                p = Braid(braid1, strands)
            else:
                if('{' not in braid):
                    strands = max(list(map(lambda x: abs(x), braid1)))+1
                    p = Braid(braid1, strands)
                ttk.Label(self.strand_default, text="= "+ str(p.strands),
                    font=(font_style, font_size)).pack(anchor='w')
        except ValueError:
            strand_check_message += "Bad strand input."
        except UnboundLocalError:
            pass

        if(strand_check_message!=""):
            ttk.Label(self.strand_check, text=strand_check_message,
                font=(font_style, font_size), background="pink").pack()

        try:
            return p
        except Exception:
            pass


# Class for color inputs
class Color(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        braid = self.parent.braid_str.get()

        # Configure the two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Add title
        ttk.Label(
            self, text='''Colors''',
            font=(font_style, font_size), background='yellow').grid(
            column=0, row=0, columnspan=2)

        # Configure frame for printing defaults
        self.one_color_default = tk.Frame(self)
        self.multi_color_default = tk.Frame(self)
        self.color_check = tk.Frame(self)

        # Configure variables to hold inputs
        self.color_choice = tk.IntVar(value=0)
        self.color_str = tk.StringVar()

        # Configure and place radio buttons and entries
        # One color
        self.use_one_color = ttk.Radiobutton(self, text="One color",
            variable=self.color_choice,
            style='C.TRadiobutton', value=1, command=self.get_col_braid)
        self.use_one_color.grid(column=0, row=1, pady=10, sticky='W')
        # One per knot
        self.use_one_per_knot = ttk.Radiobutton(self, text="One per knot",
            variable=self.color_choice,
            style='C.TRadiobutton', value=2, command=self.get_col_braid)
        self.use_one_per_knot.grid(column=0, row=2, pady=10, sticky='W')
        # Custom
        self.use_custom = ttk.Radiobutton(self, text="Custom: ",
            variable=self.color_choice,
            style='C.TRadiobutton', value=3, command=self.get_col_braid)
        self.use_custom.grid(column=0, row=3, pady=10, sticky='W')
        ttk.Entry(self, textvariable=self.color_str,
            font=(font_style, font_size)).grid(
            column=1, row=3, padx=0, pady=10, sticky='W')
        # Example of a custom entry
        ttk.Label(self, text="Example: '0 0 1' for 3 knots",
            font=(font_style, font_size), background='cyan').grid(
            column=1, row=4, pady=10, sticky='W')

    # Make a colored braid and return error messages
    # Command for getting the coloured braid
    def get_col_braid(self) -> ColBraid:
        self.color_check.destroy()
        self.multi_color_default.destroy()
        self.one_color_default.destroy()
        self.color_check = tk.Frame(self)
        self.multi_color_default = tk.Frame(self)
        self.one_color_default = tk.Frame(self)

        # Place frames for various defaults and error messages
        self.color_check.grid(column=0, row=5, pady=10)
        self.one_color_default.grid(column=1, row=1, pady=10, sticky='W')
        self.multi_color_default.grid(column=1, row=2, pady=10, sticky='W')

        self.parent.compute_cyc()
        p = self.parent.strands.make_braid()

        def print_col_list(lst: List[int]):
            a = ""
            for i in lst:
                a += str(i) + " "
            return a

        try:
            color_option = self.color_choice.get()
            assert color_option != 0, AssertionError

            if(color_option == 1):
                col_list = [0]*p.ct_knots
                ttk.Label(self.one_color_default,
                    text="= "+print_col_list(col_list),
                    font=(font_style, font_size)).pack(anchor='w')
            elif(color_option == 2):
                col_list = list(range(p.ct_knots))
                ttk.Label(self.multi_color_default,
                    text="= "+print_col_list(col_list),
                    font=(font_style, font_size)).pack(anchor='w')
            else:
                col_list = self.color_str.get()
                col_list = [int(x) for x in col_list.split(" ")]

            col_signs = [1]*(max(col_list)+1)

            p = ColBraid(p.braid, p.strands, col_list)
            complete_choice = self.parent.complete_graph.get()
            if(complete_choice==0):
                p, col_signs = find_min_perm(p, col_signs, 50)
            else:
                p, col_signs = find_min_perm_complete(p, col_signs, 50)
            return p

        except ValueError:
            ttk.Label(self.color_check, text="Bad color input",
                font=(font_style, font_size), background="pink").pack()
        except AssertionError:
            ttk.Label(self.color_check, text="Specify colors",
                font=(font_style, font_size), background="pink").pack()

    # Makes the graph for the colored braid derived from the color inputs
    def get_graph(self):
        self.color_check.destroy()
        self.multi_color_default.destroy()
        self.one_color_default.destroy()
        self.color_check = tk.Frame(self)
        self.multi_color_default = tk.Frame(self)
        self.one_color_default = tk.Frame(self)

        # Place frames for various defaults and error messages
        self.color_check.grid(column=0, row=5, pady=10)
        self.one_color_default.grid(column=1, row=1, pady=10, sticky='W')
        self.multi_color_default.grid(column=1, row=2, pady=10, sticky='W')

        self.parent.compute_cyc()
        p = self.parent.strands.make_braid()

        def print_col_list(lst: List[int]):
            a = ""
            for i in lst:
                a += str(i) + " "
            return a

        try:
            color_option = self.color_choice.get()
            assert color_option != 0, AssertionError

            if(color_option == 1):
                col_list = [0]*p.ct_knots
                ttk.Label(self.one_color_default,
                    text="= "+print_col_list(col_list),
                    font=(font_style, font_size)).pack(anchor='w')
            elif(color_option == 2):
                col_list = list(range(p.ct_knots))
                ttk.Label(self.multi_color_default,
                    text="= "+print_col_list(col_list),
                    font=(font_style, font_size)).pack(anchor='w')
            else:
                col_list = self.color_str.get()
                col_list = [int(x) for x in col_list.split(" ")]

            col_signs = [1]*(max(col_list)+1)

            p = ColBraid(p.braid, p.strands, col_list)
            
            complete_choice = self.parent.complete_graph.get()
            if(complete_choice==0):
                p, col_signs = find_min_perm(p, col_signs, 50)
                graph = p.make_graph(col_signs)
            else:
                p, col_signs = find_min_perm_complete(p, col_signs, 50)
                graph= p.make_graph_complete(col_signs)

            return graph

        except ValueError:
            ttk.Label(self.color_check, text="Bad color input",
                font=(font_style, font_size), background="pink").pack()
        except AssertionError:
            ttk.Label(self.color_check, text="Specify colors",
                font=(font_style, font_size), background="pink").pack()


# Class for signature inputs
class Signature(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        braid = self.parent.braid_str.get()

        # Configure the two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Add title
        ttk.Label(
            self, text='''Signature inputs''',
            font=(font_style, font_size), background='yellow').grid(
            column=0, row=0, columnspan=2)

        # Configure frame for printing defaults
        self.signature_default = tk.Frame(self)
        self.signature_check = tk.Frame(self)

        # Configure variables to hold inputs
        self.signature_choice = tk.IntVar(value=0)
        self.signature_str = tk.StringVar()

        # Configure and place radio buttons and entries
        # Default
        self.use_defaults = ttk.Radiobutton(self, text="Default",
            variable=self.signature_choice,
            style='C.TRadiobutton', value=1, command=self.get_omega)
        self.use_defaults.grid(column=0, row=1, pady=10, sticky='W')
        # Custom
        self.use_custom = ttk.Radiobutton(self, text="Custom: ",
            variable=self.signature_choice,
            style='C.TRadiobutton', value=2, command=self.get_omega)
        self.use_custom.grid(column=0, row=2, pady=10, sticky='W')
        ttk.Entry(self, textvariable=self.signature_str,
            font=(font_style, font_size)).grid(
            column=1, row=2, padx=0, pady=10, sticky='W')
        # Example of a custom entry
        ttk.Label(self, text="Example: '1/2 1/3' means '(pi, 2*pi/3)'",
            font=(font_style, font_size), background='cyan').grid(
            column=1, row=3, pady=10, sticky='W')

    # Get the signature input and return error messages
    def get_omega(self) -> Braid:
        # Destroy and reinitialize message frames
        self.signature_default.destroy()
        self.signature_check.destroy()
        self.signature_check = tk.Frame(self)
        self.signature_default = tk.Frame(self)

        self.signature_default.grid(column=1, row=1, pady=10, sticky='W')
        self.signature_check.grid(column=0, row=5, pady=10, columnspan=2)

        signature_inputs = self.signature_str.get()

        graph = self.parent.color.get_graph()

        try:
            signature_option = self.signature_choice.get()
            assert signature_option != 0, AssertionError

            if(signature_option == 1):
                omega = [complex(-1, 0)]*graph.colors
                ttk.Label(self.signature_default, text="= "+ "1/2 "*graph.colors,
                    font=(font_style, font_size)).pack(anchor='w')
            else:
                complex_tuple = [eval(x) for x in
                    signature_inputs.strip().split(" ")]
                for c in complex_tuple:
                    if(c==1.0):
                        ttk.Label(self.signature_check,
                            text="2*pi is not allowed.",
                            font=(font_style, font_size),
                            background='pink').pack(anchor='w')
                omega = [complex(cos(2*pi*x), sin(2*pi*x))
                    for x in complex_tuple]

        except AssertionError:
            ttk.Label(self.signature_check, text="Specify signature inputs",
                    font=(font_style, font_size),
                    background='pink').pack(anchor='w')
        except ValueError:
            ttk.Label(self.signature_check, text="Bad signature inputs",
                    font=(font_style, font_size),
                    background='pink').pack(anchor='w')

        try:
            return omega
        except Exception:
            pass


# Class for Casson Gordon inputs
class Casson_Gordon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Configure the two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Add title
        ttk.Label(
            self, text='''Casson-Gordon invariants''',
            font=(font_style, font_size), background='yellow').grid(
            column=0, row=0, columnspan=2)

        # Configure variables to hold inputs
        self.framing = tk.StringVar()
        self.q_ni_cg = tk.StringVar()

        # Configure and place labels for inputs and and examples
        ttk.Label(self, text="Framing:",
            font=(font_style, font_size)).grid(
            column=0, row=1, padx=0, pady=10)
        ttk.Label(self, text="Example: '1 0 -2'."+
            " Framing = self-linking numbers of knots.",
            font=(font_style, font_size), background='cyan').grid(
            column=0, row=2, columnspan=2, padx=0, pady=10)
        ttk.Label(self, text="q, n_i tuple:",
            font=(font_style, font_size)).grid(
            column=0, row=3, padx=0, pady=10)
        ttk.Label(self, text="Example: '5, 2 3 2' means q = 5, n_1 = 3."+
            " See paper.",
            font=(font_style, font_size), background='cyan').grid(
            column=0, row=4, columnspan=2, padx=0, pady=10)

        # Configure and place entry boxes
        ttk.Entry(self, textvariable=self.framing,
            font=(font_style, font_size)).grid(
            column=1, row=1, padx=0, pady=10, sticky='W')
        ttk.Entry(self, textvariable=self.q_ni_cg,
            font=(font_style, font_size)).grid(
            column=1, row=3, padx=0, pady=10, sticky='W')

        self.casson_gordon_frame = tk.Frame(self)

    def compute_casson_gordon(self):
        self.casson_gordon_frame.destroy()
        self.casson_gordon_frame = tk.Frame(self)
        self.casson_gordon_frame.grid(
            column=0, row=5, columnspan=2, padx=0, pady=10)

        self.casson_gordon_frame.grid_columnconfigure(0)
        self.casson_gordon_frame.grid_columnconfigure(1)

        ttk.Label(self.casson_gordon_frame, text="Casson-Gordon invariant:",
            font=(font_style, font_size)).grid(
            column=0, row=0, padx=0, pady=10)

        framing_str = self.framing.get()
        q_ni_cg_str = self.q_ni_cg.get()

        framing_val = [int(x) for x in framing_str.split(" ")]
        q = int(q_ni_cg_str.strip()[0])
        ni_tuple_str = q_ni_cg_str[q_ni_cg_str.find(",")+1:].strip().split(" ")
        ni_tuple = [int(x) for x in ni_tuple_str]

        p = self.parent.strands.make_braid()

        ttk.Label(self.casson_gordon_frame,
            text=str(casson_gordon(framing_val, q, ni_tuple, p)),
            font=(font_style, font_size)).grid(
            column=1, row=0, padx=0, pady=10)

    def get_casson_gordon(self):
        try:
            self.compute_casson_gordon()
        except (ValueError, AttributeError):
            self.casson_gordon_frame.destroy()
            self.casson_gordon_frame = tk.Frame(self)
            ttk.Label(self, text="Check inputs",
                font=(font_style, font_size), background='pink').grid(
                column=0, row=5, columnspan=2, padx=0, pady=10)

# Executing everything
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Clasper")

    # Get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Find the center point
    center_x = int(screen_width/2)
    center_y = int(screen_height/2)

    window_width = screen_width
    window_height = screen_height

    # Set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{0}')

    root.state('zoomed')

    clasper_canvas = tk.Canvas(root)
    hbar = tk.Scrollbar(root, orient='horizontal',
        command=clasper_canvas.xview)
    scrollbar = tk.Scrollbar(root, orient='vertical',
        command=clasper_canvas.yview)

    hbar.pack(side="bottom", fill="both")
    clasper_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="both")

    clasper_canvas['yscrollcommand'] = scrollbar.set
    clasper_canvas['xscrollcommand'] = hbar.set

    clasper = Clasper(clasper_canvas)
    
    def onCanvasConfigure(e):
        clasper_canvas.configure(scrollregion=clasper_canvas.bbox("all"))
        clasper_canvas.itemconfig('frame',
            height=2800,
            width=3000)

    clasper_canvas.create_window(0, 0,
            height=2800,
            width=3000,
        window=clasper, anchor="nw", tags="frame")

    clasper_canvas.bind("<Configure>", onCanvasConfigure)

    clasper_canvas.configure(scrollregion=clasper_canvas.bbox("all"))
    clasper_canvas.itemconfig('frame',
            height=2800,
            width=3000)

    def on_mousewheel(event):
        clasper_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_shift_mousewheel(event):
        clasper_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
    
    root.bind_all("<MouseWheel>", on_mousewheel)
    root.bind_all("<Shift-MouseWheel>", on_shift_mousewheel)

    root.bind('<Return>', clasper.compute_with_defaults)

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()


# Setting up the entry for strands

        """ttk.Label(
            self, text='Number of Strands:',
            font=(font_style, font_size)).grid(column=0, row=2, pady=10)
        self.strand_str = tk.StringVar()
        ttk.Entry(self, textvariable=self.strand_str,
            font=(font_style, font_size)).grid(
            column=1, row=2, padx=0, pady=10, sticky='W', columnspan=3)"""
    
        # Set up entry for the colour list
        """ttk.Label(self, text='Colours (start from 0, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=5, pady=10)
        self.colour_list = tk.StringVar()
        ttk.Entry(self, textvariable=self.colour_list,
            font=(font_style, font_size)).grid(
            column=1, row=5, padx=0, pady=10, sticky='W', columnspan=3)"""

        # Set up entry for orientations of colours
        """ttk.Label(self, text='Orientations (+1/-1, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=6, pady=10)
        self.colour_signs = tk.StringVar()
        ttk.Entry(self, textvariable=self.colour_signs,
            font=(font_style, font_size)).grid(
            column=1, row=6, padx=0, pady=10, sticky='W', columnspan=3)
        """

        # Set up entry for complex tuple
        """ttk.Label(self, text='Signature input,'+
            'space sep\n (1/3 means 2*pi/3, BFD):',
            font=(font_style, font_size)).grid(
            column=0, row=7, pady=10)
        self.cplx_tuple = tk.StringVar()
        ttk.Entry(self, textvariable=self.cplx_tuple,
            font=(font_style, font_size)).grid(
            column=1, row=7, padx=0, pady=10, sticky='W', columnspan=2)"""
