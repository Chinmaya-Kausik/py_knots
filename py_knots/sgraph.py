import math
from typing import List, Tuple, Callable
from dataclasses import dataclass
from braid import *


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
    vve: Callable[[SVertex, SVertex], List[SEdge]]
    ve: Callable[[SVertex], List[SEdge]]
    col_signs: List[int]

    # Add a new edge to the front of the graph. Produces a new graph.
    def add_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve(init, term)), typ, col)

        def new_vve(initial, terminal) -> List[SEdge]:
            if((initial == init) and (terminal == term)):
                return vve(initial, terminal) + [new_edge]
            else:
                return vve(initial, terminal)

        def new_ve(v) -> List[SEdge]:
            if((v==init) or (v==term)):
                return ve(v) + [new_edge]
            else:
                return ve(v)

        self.edges.append(new_edge)
        self.vve = new_vve
        self.ve = new_ve

    # Add a new edge to the back of the graph. Produces a new graph.
    def add_init_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve(init, term)), typ, col)

        def new_vve(initial, terminal) -> List[SEdge]:
            if((initial == init) and (terminal == term)):
                return [new_edge] + vve(initial, terminal)
            else:
                return vve(initial, terminal)

        def new_ve(v) -> List[SEdge]:
            if((v==init) or (v==term)):
                return [new_edge] + ve(v)
            else:
                return ve(v)

        self.edges = [new_edge] + self.edges
        self.vve = new_vve
        self.ve = new_ve
