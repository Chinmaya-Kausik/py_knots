from braid import *
from sgraph import *
from typing import List
from numpy import random
import copy


# Searches n random permutations for n=tries to find 
# the one with the minimal homology basis among them
# for connected spline graphs
def find_min_perm(p: ColBraid, col_signs: List[int],
        tries: int) -> (ColBraid, List[int]):
    colors = max(p.col_list)+1
    col = list(range(colors))

    col_list = copy.deepcopy(p.col_list)
    graph = p.make_graph(col_signs)
    size = len(graph.hom_basis)
    good_perm = col

    for i in range(tries):
        perm = random.permutation(col)
        new_col_list = [perm[j] for j in col_list]
        new_col_signs = [col_signs[j] for j in perm]

        new_p = ColBraid(p.braid, p.strands, new_col_list)
        new_graph = new_p.make_graph(new_col_signs)

        if(len(new_graph.hom_basis) < size):
            size = len(new_graph.hom_basis)
            good_perm = perm

    new_col_list = [good_perm[i] for i in col_list]
    new_col_signs = [col_signs[i] for i in good_perm]
    new_p = ColBraid(p.braid, p.strands, new_col_list)

    return (new_p, new_col_signs)


# Searches n random permutations for n=tries to find 
# the one with the minimal homology basis among them
# for spline graphs with a complete graph on colors
def find_min_perm_complete(p: ColBraid, col_signs: List[int],
        tries: int) -> (ColBraid, List[int]):
    colors = max(p.col_list)+1
    col = list(range(colors))

    col_list = copy.deepcopy(p.col_list)
    graph = p.make_graph_complete(col_signs)
    size = len(graph.hom_basis)
    good_perm = col

    for i in range(tries):
        perm = random.permutation(col)
        new_col_list = [perm[j] for j in col_list]
        new_col_signs = [col_signs[j] for j in perm]

        new_p = ColBraid(p.braid, p.strands, new_col_list)
        new_graph = new_p.make_graph_complete(new_col_signs)

        if(len(new_graph.hom_basis) < size):
            size = len(new_graph.hom_basis)
            good_perm = perm

    new_col_list = [good_perm[i] for i in col_list]
    new_col_signs = [col_signs[i] for i in good_perm]
    new_p = ColBraid(p.braid, p.strands, new_col_list)

    return (new_p, new_col_signs)





