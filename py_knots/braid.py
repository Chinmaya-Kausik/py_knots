import math
from typing import List, Tuple, Callable, Dict
from dataclasses import dataclass
from sgraph import *
from functools import cached_property

"""
----- Generates the spline graph for a braid. 
----- Generalized Seifert matrices are computed in sgraph.py. 
"""


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
    return lst[0:n] + [lst[n+1], lst[n]] + lst[n+2:]


# Class for braids. Methods related to its permutation.
# For generating spline graphs, we use ColBraid
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

    # Number of different knots in the link.
    @cached_property
    def ct_knots(self) -> int:
        return len(self.cycle_decomp)


# Class for coloured braids. Generates spline graphs.
# Extra data is col_list - a list of colours for each knot.
@dataclass(frozen=True)
class ColBraid(Braid):
    col_list: List[int]

    # Cycles grouped by color.
    @cached_property
    def cyc_by_color(self) -> List[List[List[int]]]:
        cyc_decomp = self.cycle_decomp
        cyc_by_col = [[] for i in range(max(self.col_list)+1)]

        for color in range(0, max(self.col_list)+1):
            for i in range(0, len(cyc_decomp)):
                if self.col_list[i]==color:
                    cyc_by_col[color] += [cyc_decomp[i]]

        return cyc_by_col

    # Generates the vertices for the spline graph.
    @cached_property
    def vertices(self) -> List[SVertex]:
        vert_list = []
        cyc_by_col = self.cyc_by_color

        for color in range(len(cyc_by_col)):
            for cyc in cyc_by_col[color]:
                for vert in cyc:
                    vert_list.append(SVertex(len(vert_list), color))

        return vert_list

    # The permutation of vertices before the braid is applied.
    # This is non-trivial because vertices are generated grouped by color,
    # and not by the initial permutation.
    @cached_property
    def init_vert_perm(self) -> List[SVertex]:
        vert_perm = list(range(self.strands))
        vertices = self.vertices

        flat_cyc_by_color = []
        for color in self.cyc_by_color:
            tally = []
            for cyc in color:
                tally += cyc 
            flat_cyc_by_color += sorted(tally)

        for vert_ind in range(self.strands):
            vert_perm[flat_cyc_by_color[vert_ind]-1] = vertices[vert_ind]

        return vert_perm

    # Initializes an SGraph with only the right vertices and no edges.
    def init_graph(self, col_signs: List[int]) -> SGraph:
        vert = self.vertices

        empty_vve = {}
        empty_ve = {}

        for i in range(len(vert)):
            for j in range(len(vert)):
                if(j>i):
                    empty_vve[(vert[i], vert[j])] = []

        for v in vert:
            empty_ve[v] = []

        return SGraph(vert, [], empty_vve, empty_ve, len(col_signs), col_signs)

    # Goes through braid generators, adding clasps and half-twists.
    def add_clasps_hts(self, graph: SGraph) -> SGraph:

        braid1 = self.braid
        vert_perm = self.init_vert_perm

        while(braid1 != []):

            """First find the upper and lower strands. Our convention is that
            __   __
              \ /
               /
            __/ \__
            is considered +1.
            So here, the strand that starts at the top is the lower one.
            """
            i = abs(braid1[0])
            sgn = sign(braid1[0])

            if(sgn == 1):
                below = i
            else:
                below = i-1
            above = 2*i-1-below
            upper = vert_perm[above]
            lower = vert_perm[below]

            # Half-twist if the current transposition is within the same colour
            if(upper.col == lower.col):
                braid1 = braid1[1:]
                graph.add_edge(vert_perm[i-1], vert_perm[i], sgn, upper.col)

            # Move on if the lower strand just pulls down to a lower colour
            elif(lower.col < upper.col):
                braid1 = braid1[1:]
                vert_perm = transpose(i-1, vert_perm)

            # Otherwise (if the upper strand has a lower colour), add clasps
            else:
                clasps = []
                # Find clasp vertices
                for i_vert in range(0, len(vert_perm)):
                    if((i_vert < i-1) and
                        (vert_perm[i_vert].col > upper.col) and
                    (vert_perm[i_vert].num < lower.num)):
                        clasps += [vert_perm[i_vert]]

                # Add left clasps
                for j in range(0, len(clasps)):
                    graph.add_edge(upper, clasps[j], -2, upper.col)

                # Add main clasp
                graph.add_edge(upper, lower, sgn*2, upper.col)

                # Add right clasps
                for j in range(0, len(clasps)):
                    graph.add_edge(upper, clasps[j], 2, upper.col)

                braid1 = braid1[1:]
                vert_perm = transpose(i-1, vert_perm)

        return graph

    def make_graph(self, col_signs: List[int]) -> SGraph:
        graph = self.init_graph(col_signs)
        self.add_clasps_hts(graph)
        graph.clean_graph()
        graph.colors_connected()
        graph.make_complete()
        return graph


    




        



    












