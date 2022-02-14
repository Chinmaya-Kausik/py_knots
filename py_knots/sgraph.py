import math
from typing import List, Tuple, Callable, Dict
from functools import cached_property
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


def check_loop(lst: List[SEdge]) -> bool:
    is_loop = True 
    for i in range(len(lst)):
        is_loop = is_loop and(lst[i].terminal == lst[i+1].initial)
    return is_loop and (lst[-1].terminal == lst[0].initial)


# Class for spline graphs of clasp complexes
@dataclass
class SGraph:
    vert: List[SVertex]
    edges: List[SEdge]
    vve: Dict[Tuple[SVertex, SVertex], List[SEdge]]
    ve: Dict[SVertex, List[SEdge]]
    colors: int
    col_signs: List[int]

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

    # Gives a value to a lift (or not) of a vertex.
    # If not lifted, the value is just its index.
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
        self.vve[(init, term)][-1]

    def local_graph_hom_basis(self, col: int) -> List:
        pass


# Class for loops in spline graphs.
@dataclass
class Loop:
    edges: List[SEdge]

    def __post_init__(self):
        assert check_loop(edges), "This list does not form a loop: " + str(edges)