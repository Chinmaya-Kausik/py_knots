from braid import *
from sgraph import *
from pres_mat import *
from visualization import *
from col_perm import *
from casson_gordon import *

p = ColBraid([2, 3, -2, 3, 1, 2, 3], 4, [0, 1, 2])

p = Braid([1, 10], 11)

print(p.cycle_decomp, p.braid, p.strands)

"""
col_list = [0]*p.ct_knots
col_signs = [1]
"""
col_list = list(range(p.ct_knots))
print("Color list:", col_list)
col_signs = [1]*(p.ct_knots)
print("Color signs: ", col_signs)
print(" ")

p = ColBraid(p.braid, p.strands, col_list)
p, col_signs = find_min_perm(p, col_signs, 500)
graph = p.make_graph(col_signs)

verti, edges_col, edge_dict = graph.find_col_graph()
print("Graph = ", verti, edges_col, edge_dict)
print("MST = ", find_mst(verti, edges_col, edge_dict))
visualize_braid(p)

"""graph.print_data()
framing = [-4, 2]
q=5
char_list =[4, 2]

pm = presentation_matrix(graph)
print("Variables", pm.variables)

print(casson_gordon(framing, q, char_list, p))
s = symbols("s")
k = symbols("k")
cg_var, cg_sym = casson_gordon_symbolic(framing, p)
print(cg_sym.subs(cg_var[0], 2*s).subs(cg_var[1], s))
print(graph.linking_matrix([0, 0]))"""


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


"""

visualize_clasp_complex(graph)
pm = presentation_matrix(graph)


print(pm.conway_potential_function(graph))
print(pm.multivar_alexander_poly(graph))
print("\n\nsignature", pm.signature([complex(-1,0)]*graph.colors))"""

"""pathex=['C:\\Users\\chinm\\Documents\\GitHub\\py_knots\\py_knots'],
             binaries=[],
             datas=[],
             hiddenimports=['sgraph', 'braid', 'col_perm',
             'visualization', 'casson_gordon', 'pres_mat'],"""