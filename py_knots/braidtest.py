from braid import *
from sgraph import *
from pres_mat import *
from visualization import *
from col_perm import *

p = ColBraid([2, 3, -2, 3, 1, 2, 3], 4, [0, 1, 2])


def link_info(braid: str) -> Braid:
        Message = ""
        try:
            start = braid.index('{')+1
            strands = int(braid[start])
            new_braid = braid[start:]
            braid1 = new_braid[
                new_braid.index('{')+1: new_braid.index('}')].split(',')
            braid1 = list(map(lambda x: int(x), braid1))
        except ValueError:
            Message += "Invalid Link Info input. "
            braid1 = []
            strands = 0

        return Braid(braid1, strands)

braid = "{5, {-1, -2, -2, -1, -3, -4, 3, -2, -2, 3, 4, -3}}"
p = link_info(braid)
print(p.cycle_decomp, p.braid, p.strands)

"""
col_list = [0]*p.ct_knots
col_signs = [1]
"""
col_list = list(range(p.ct_knots))
print(col_list)
col_signs = [1]*(p.ct_knots)
print(col_signs)

p = ColBraid(p.braid, p.strands, col_list)
p, col_signs = find_min_perm(p, col_signs, 500)
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

print(len(graph.hom_basis))
"""

visualize_clasp_complex(graph)
pm = presentation_matrix(graph)


print(pm.conway_potential_function(graph))
print(pm.multivar_alexander_poly(graph))
print("\n\nsignature", pm.signature([complex(-1,0)]*graph.colors))"""