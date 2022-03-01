from braid import *
from sgraph import *
from pres_mat import *
from inputs import *
from visualization import *
from col_perm import *

p = ColBraid([2, 3, -2, 3, 1, 2, 3], 4, [0, 1, 2])


braid = "{2, {1, 1, 1, 1}}"
p = link_info(braid)
print(p.cycle_decomp, p.braid, p.strands)


col_list = [0]*p.ct_knots
col_signs = [1]

"""col_list = list(range(p.ct_knots))
print(col_list)
col_signs = [1]*(p.ct_knots)
print(col_signs)"""

p = link_info_col(braid, col_list)
p, col_signs = find_min_perm(p, col_signs, 50)
graph = p.make_graph(col_signs)
visualize_braid(p)

"""
print("Braid", p.braid)
print(p.cyc_by_color)
print(p.vertices)
print(p.init_vert_perm)
new_p = ColBraid(p.braid, p.strands, new_col_list)

print("\nChecking stuff now")
graph = p.init_graph(col_signs)
p.add_clasps_hts(graph).clean_graph()
graph.print_data()
print(graph.col_first_verts)
print(graph.all_single_color_hom_bases)
print(graph.all_local_graph_hom_bases)
print(graph.complete_graph_hom_basis)
print(graph.hom_basis)
loop1 = graph.hom_basis[0]
loop2 = graph.hom_basis[1]
print(graph.linking_number(loop1, loop2, [-1]))
"""

graph.print_data()
print(graph.hom_basis)


visualize_clasp_complex(graph)
pm = presentation_matrix(graph)


print(pm.conway_potential_function(graph))
print(pm.multivar_alexander_poly(graph))
print("\n\nsignature", pm.signature([complex(-1,0)]*graph.colors))