import math
from typing import List, Tuple, Callable, Dict
from dataclasses import dataclass


# Class for vertices
@dataclass(frozen=True)
class SVertex:
    num: int
    col: int


# Class for edges
@dataclass(frozen=True)
class SEdge:
    initial: SVertex
    terminal: SVertex
    num: int
    typ: int
    col: int


# Class for spline graphs of clasp complexes
@dataclass
class SGraph:
    vert: List[SVertex]
    edges: List[SEdge]
    vve: Dict[Tuple[SVertex, SVertex], List[SEdge]]
    ve: Dict[SVertex, List[SEdge]]
    col_signs: List[int]

    # Add a new edge to the front of the graph. Produces a new graph.
    def add_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = self.vve[(init, term)] + [new_edge]
        self.ve[init] = self.ve[init] + [new_edge]
        self.ve[term] = self.ve[term] + [new_edge]

    # Add a new edge to the back of the graph. Produces a new graph.
    def add_init_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = [new_edge] + self.vve[(init, term)]
        self.ve[init] = [new_edge] + self.ve[init]
        self.ve[term] = [new_edge] + self.ve[term]

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
        tally = list(range(max(self.col_list)+1))
        col_1st_verts = []

        for v in vert:
            if(v.col in tally):
                col_1st_verts.append(v)
                tally = tally[1:]

        return col_1st_verts

    # Makes sure each Seifert surface is connected
    def colors_connected(self):
        vert = self.vert

        while(len(vert) != 1):
            v0 = vert[0]
            v1 = vert[1]
            if(v0.col == v1.col):
                if(vve[(v0, v1)] == []):
                    self.add_edge(v0, v1, 1, v0.col)
                    self.add_edge(v0, v1, -1, v0.col)
            vert = vert[1:]

    # Makes sure the graph across colors is complete
    def make_complete(self):
        v_col = self.col_first_verts
        for color1 in range(len(v_col)):
            for color2 in range(len(v_col)):
                if(color1 < color2):
                    if(self.vve[(v_col[color1], v_col[color2])] == []):
                        graph.add_edge(v_col[color1], v_col[color2], 2, color1)
                        graph.add_edge(v_col[color1], v_col[color2], -2, color1)
    
