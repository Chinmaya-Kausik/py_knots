from sgraph import *
from braid import *
from sympy import *
import copy
from typing import List, Tuple, Callable, Dict, Set
import cmath
from math import pi, cos, sin
import numpy as np
from numpy.linalg import eigh
from pres_mat import *
from sympy import *


def casson_gordon(framing: List[int], character_q: int, char_list: List[int],
        p_braid: Braid):

    col_list = list(range(p_braid.ct_knots))

    p = ColBraid(p_braid.braid, p_braid.strands, col_list)
    col_signs = [1]*(p_braid.ct_knots)

    graph = p.make_graph_complete(col_signs)
    pm = presentation_matrix(graph)

    q = float(character_q)
    for i in range(graph.colors):
        assert 0<char_list[i]<q, "Bad character input"
    omega = []

    for i in range(graph.colors):
        n_i = float(char_list[i])
        omega.append(complex(cos(2*pi*n_i/q), sin(2*pi*n_i/q)))

    signat = pm.signature(omega)
    link_mat = graph.linking_matrix(framing)

    casson_gordon = signat

    for i in range(graph.colors):
        for j in range(i+1, graph.colors):
            casson_gordon -= link_mat[i][j]

    eig_val, eig_vect = eigh(link_mat)
    sgn_link_mat = 0
    for e in eig_val:
        if(e>0):
            sgn_link_mat -= 1
        else:
            sgn_link_mat += 1
    casson_gordon -= sgn_link_mat

    for i in range(graph.colors):
        for j in range(graph.colors):
            n_i = float(char_list[i])
            n_j = float(char_list[j])

            casson_gordon += (2*(q-n_i)*n_j*link_mat[i][j])/(q**2)

    return casson_gordon


def casson_gordon_symbolic(framing: List[int], p_braid: Braid):
    col_list = list(range(p_braid.ct_knots))

    p = ColBraid(p_braid.braid, p_braid.strands, col_list)
    col_signs = [1]*(p_braid.ct_knots)

    graph = p.make_graph_complete(col_signs)
    pm = presentation_matrix(graph)

    q = symbols("q")

    cg_var = list(range(graph.colors))

    for i in range(graph.colors):
        cg_var[i] = eval("""symbols("n{}")""".format(i))

    link_mat = graph.linking_matrix(framing)

    casson_gordon = 0

    for i in range(graph.colors):
        for j in range(i+1, graph.colors):
            casson_gordon -= link_mat[i][j]

    eig_val, eig_vect = eigh(link_mat)
    sgn_link_mat = 0
    for e in eig_val:
        if(e>0):
            sgn_link_mat -= 1
        else:
            sgn_link_mat += 1
    casson_gordon -= sgn_link_mat

    for i in range(graph.colors):
        for j in range(graph.colors):
            n_i = cg_var[i]
            n_j = cg_var[j]

            casson_gordon += (2*(q-n_i)*n_j*link_mat[i][j])/(q**2)

    return (cg_var, simplify(casson_gordon))