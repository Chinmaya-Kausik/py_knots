import math
from typing import List, Tuple, Callable
from dataclasses import dataclass
from sgraph import *
from functools import cached_property


# Custom slicing
def slice(list1, a, b):
    if(a>=b):
        return []
    else:
        return list1[a:b]


# Custom sign function
def sign(n: int):
    if(n>0):
        return 1
    else:
        return -1


# Transposes the nth and (n+1)th indices in a list
def transpose(n: int, lst: List) -> List:
    lst[0:n] + [lst[n+1], lst[n]] + lst[n+2:]


# Class for braids. Method for making spline graphs.
@dataclass(frozen=True)
class Braid:
    braid: List[int]
    strands: int

    # Finds the permutation of a braid
    @cached_property
    def braid_to_perm(self) -> List[int]:

        # Initial identity permutation
        perm = list(range(1, self.strands+1))

        # Executes all transpositions
        for j in range(0, len(self.braid)):
            i = abs(self.braid[j])
            perm = slice(perm, 0, i-1) + [perm[i], perm[i-1]] + \
                            slice(perm, i+1, len(perm))

        return perm

    # Finds the cycle decomposition for a braid
    @cached_property
    def cycle_decomp(self) -> List[List[int]]:

        perm = self.braid_to_perm
        n = self.strands
        tally = list(range(1, n+1))  # Tally for all elements being permuted#
        cyc_decomp = []

        # Makes cycles until all elements are exhausted
        while(tally != []):

            i = tally[0]
            cyc = [i]

            # Constructs one cycle starting at i
            while(perm[i-1] not in cyc):
                cyc = cyc+[perm[i-1]]
                i = perm[i-1]

            cyc_decomp += [cyc]
            tally = [i for i in tally if i not in cyc]

        return cyc_decomp

    @cached_property
    def ct_components(self) -> int:
        return len(self.cycle_decomp)

    def gen_vertices(self, col_list: List[int]) -> List[SVertex]:
        cyc = self.cycle_decomp
        vertices = []

        for color in range(0, max(col_list)+1):
            for i in range(0, len(cyc)):
                if col_list[i]==color:
                    vertices.append(SVertex(len(vertices), color))

        return vertices

    # Goes through braid generators, adding clasps and half-twists.
    def graph_maker(self, vert_perm: List[SVertex], graph: SGraph) -> SGraph:

        braid1 = self.braid
        while(braid1 != []):

            i = abs(braid.head)

            # Half-twist if the current transposition is within the same colour.
            if(vert_perm[i].col == vert_perm[i-1].col):
                braid1 = braid1[1:]
                graph.add_edge(vert_perm[i-1], vert_perm[i], sign(i),
                                vert_perm[i].col)

            # Otherwise, add clasps.
            else:
                clasps = []

                if(sign(i) == 1):
                    upper = i 
                else:
                    upper = i-1

                lower = 2*i-1-upper

                for l in range(0, len(vert_perm)):
                    if((l < j-1) and (vert_perm[j].col > vert_perm[i].col) and (vert_perm[i].num)


