import math
from typing import List, Tuple, Callable
from dataclasses import dataclass


@dataclass
class SVertex:
    num: int
    col: int


@dataclass
class SEdge:
    initial: SVertex
    terminal: SVertex
    num: int
    typ: int
    col: int


@dataclass
class SGraph:
    vert: List[SVertex]
    edges: List[SEdge]
    vve: Callable[[SVertex, SVertex], List[SEdge]]
    ve: Callable[SVertex, List[SEdge]]
    col_signs: List[int]

    def add_edge(self: SGraph, init: SVertex, term: SVertex,
                 typ: int, col: int) -> SGraph:
    
        new_edge = SEdge(init, term, len(self.vve(init, term)), typ, col)

        def new_vve(initial, terminal) -> List[SEdge]:
            if((initial == init) and (terminal == term)):
                return vve(initial, terminal) ++ new_edge
            else return vve(initial, terminal)
        return SGraph(self.vert, self.edges ++ new_edge, )
