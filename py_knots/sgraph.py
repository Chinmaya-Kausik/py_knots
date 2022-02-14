import math
from typing import List, Tuple, Callable, Dict
from functools import cached_property
from dataclasses import dataclass


# Class for vertices
@dataclass(frozen=True, repr=False)
class SVertex:
    num: int
    col: int

    def __repr__(self):
        return "V({}, {})".format(self.num, self.col)


# Class for edges
@dataclass(frozen=True, repr=False)
class SEdge:
    initial: SVertex
    terminal: SVertex
    num: int
    typ: int
    col: int

    def __repr__(self):
        return "E({}, {}, {}, {}, {})".format(self.initial,
            self.terminal, self.num, self.typ, self.col)


# Class for oriented edges
@dataclass(repr=False, init=False)
class OEdge():
    sign: int

    def __init__(self, edge: SEdge, sign: int):
        self.initial = edge.initial
        self.terminal = edge.terminal

        self.num = edge.num
        self.typ = edge.typ
        self.col = edge.col
        self.sign = sign

    def __repr__(self):
        return "OE({}, {}, {}, {}, {}, {})".format(self.initial,
            self.terminal, self.num, self.typ, self.col, self.sign)

    # The true initial vertex, accounting for orientation.
    @cached_property
    def true_initial(self) -> SVertex:
        if(self.sign == 1):
            return self.initial
        else:
            return self.terminal

    # The true terminal vertex, accounting for orientation.
    @cached_property
    def true_terminal(self) -> SVertex:
        if(self.sign == 1):
            return self.terminal
        else:
            return self.initial


# Checks if a list of edges forms a loop.
def check_loop(lst: List[OEdge]) -> bool:
    is_loop = True 
    for i in range(len(lst)-1):
        is_loop = is_loop and (lst[i].true_terminal == lst[i+1].true_initial)

    return is_loop and (lst[-1].true_terminal == lst[0].true_initial)


# Class for loops in spline graphs.
@dataclass
class Loop:
    edges: List[OEdge]

    def __post_init__(self):
        assert check_loop(self.edges), "This list does not form a loop: "\
            +str(self.edges)


# Class for spline graphs of clasp complexes
@dataclass
class SGraph:
    vert: List[SVertex]
    edges: List[SEdge]
    vve: Dict[Tuple[SVertex, SVertex], List[SEdge]]
    ve: Dict[SVertex, List[SEdge]]
    colors: int
    col_signs: List[int]

    """

    ------- Tools for making the final spline graph ------

    """

    # Add a new edge to the front of the graph.
    def add_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = self.vve[(init, term)] + [new_edge]
        self.ve[init] = self.ve[init] + [new_edge]
        self.ve[term] = self.ve[term] + [new_edge]

    # Add a new edge to the back of the graph.
    def add_init_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = [new_edge] + self.vve[(init, term)]
        self.ve[init] = [new_edge] + self.ve[init]
        self.ve[term] = [new_edge] + self.ve[term]

    # Deletes an edge from the graph
    def delete_edge(self, edge: SEdge):
        self.edges.remove(edge)
        self.vve[(edge.initial, edge.terminal)].remove(edge)
        self.ve[edge.initial].remove(edge)
        self.ve[edge.terminal].remove(edge)

    # Finds and deletes a redundant pair of edges in the graph
    def delete_redundant_pair(self) -> bool:
        exists = False
        i = 0
        while(i < len(self.edges)-1):
            if((self.edges[i].initial == self.edges[i+1].initial) and
                (self.edges[i].terminal == self.edges[i+1].terminal) and
            (self.edges[i].typ == -self.edges[i+1].typ)):
                self.delete_edge(self.edges[i])
                self.delete_edge(self.edges[i])
                exists = True
            else:
                i +=1

        return exists

    # Cleans up redundant pairs of edges.
    def clean_graph(self):
        exists = True
        while(exists):
            exists = self.delete_redundant_pair()

    # Prints the abstract data of the graph
    # List of vertex indices, then edges = (init, term, type)
    def print_data(self):
        print(list(range(len(self.vert))))
        for edge in self.edges:
            print("("+ str(self.vert.index(edge.initial))+ ", " +
                str(self.vert.index(edge.terminal)) + ", " +
                str(edge.typ) + "), ", end='')

    # List of the first vertices in each color.
    @cached_property
    def col_first_verts(self) -> List[SVertex]:
        vert = self.vert
        tally = list(range(self.colors))
        col_1st_verts = []

        for v in vert:
            if(v.col in tally):
                col_1st_verts.append(v)
                tally = tally[1:]

        return col_1st_verts

    # Makes sure each Seifert surface is connected
    def colors_connected(self) -> None:
        vert = self.vert

        while(len(vert) != 1):
            v0 = vert[0]
            v1 = vert[1]
            if(v0.col == v1.col):
                if(self.vve[(v0, v1)] == []):
                    self.add_edge(v0, v1, 1, v0.col)
                    self.add_edge(v0, v1, -1, v0.col)
            vert = vert[1:]

    # Checks if two colors are connected.
    # The lower color should be the first input.
    def check_connected(self, col1: int, col2: int) -> bool:
        connected = False
        i = 0
        while((not connected) and (i<len(self.vert))):
            if(self.vert[i].col == col1):
                for v2 in self.vert:
                    if((v2.col == col2) and
                    (self.vve[(self.vert[i], v2)] != [])):
                        connected = True
                        break
            i+=1
        return connected

    # Makes sure the graph across colors is complete
    def make_complete(self):
        v_col = self.col_first_verts
        for color1 in range(len(v_col)):
            for color2 in range(len(v_col)):
                if((color1 < color2) and
                    (self.vve[(v_col[color1], v_col[color2])] == []) and
                (not self.check_connected(color1, color2))):
                    self.add_edge(v_col[color1], v_col[color2], 2, color1)
                    self.add_edge(v_col[color1], v_col[color2], -2, color1)

    """

    ------ Now moving on to generating a homology basis ------

    """

    # Gives a value to a lift (or not) of a vertex.
    # If it is not lifted (lift = 0), the value is just its index.
    # Otherwise add or subtract 0.5 depending on the direction of the lift
    def value(self, vert: SVertex, lift: int) -> float:
        assert vert in self.vert, "The vertex " + str(vert) + \
            " is not in the graph"

        if(lift == 0):
            return vert.num
        else:
            return vert.num + self.col_signs(vert.col)*0.5

    # Finds the rightmost edge between two vertices.
    def max_edge(self, init: SVertex, term: SVertex) -> SEdge:
        return self.vve[(init, term)][-1]

    # Finds the homology basis of the subgraph
    # corresponding to a given color
    def single_color_hom_basis(self, col: int) -> List[Loop]:
        hom_basis = []
        i = self.vert.index(self.col_first_verts[col])
        n = len(self.vert)

        while((i<n-1) and (self.vert[i+1].col == col)):
            v1 = self.vert[i]
            v2 = self.vert[i+1]
            m_edge = OEdge(self.max_edge(v1, v2), -1)
            for edge in self.vve[(v1, v2)][:-1]:
                o_edge = OEdge(edge, 1)

                hom_basis.append(Loop([o_edge, m_edge]))
            i+=1

        return hom_basis

    # Combines the homology bases for subgraphs for individual colors.
    def all_single_color_homology_bases(self):
        hom_basis = []
        for col in range(self.colors):
            hom_basis += self.single_color_hom_basis(col)
        return hom_basis

    # Finds the rightmost edge connecting two colors.
    # Enter the lower color first.
    def max_connector(self, col1: int, col2: int) -> SEdge:
        for edge in reversed(self.edges):
            if((edge.initial.col, edge.terminal.col) == (col1, col2)):
                return edge

    # Connects two vertices of the same color.
    def connect_vertices(self, v1: SVertex, v2: SVertex) -> List[OEdge]:
        assert v1.col == v2.col,\
            "The vertices {} {} have different colors".format(v1, v2)

        path = []
        if(v1.num > v2.num):
            num = v1.num
            while(num>v2.num):
                vert_1 = self.vert[num]
                vert_2 = self.vert[num-1]
                path.append(OEdge(self.max_edge(vert_2, vert_1), -1))
                num -= 1
        else:
            num = v1.num
            while(num<v2.num):
                vert_1 = self.vert[num]
                vert_2 = self.vert[num+1]
                path.append(OEdge(self.max_edge(vert_1, vert_2), -1))
                num += 1

    # Completes an edge into a loop
    def make_loop(edge: SEdge) -> Loop:
        v1 = edge.initial
        v2 = edge.terminal
        assert v1.col != v2.col,\
            "The endpoints {} {} have the same color".format(v1, v2)
        pass

    # Finds the homology basis corresponding
    # to the local graph between two given colors.

