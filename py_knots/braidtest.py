from braid import *

p = Braid([2, 3, -2, 3, 1, 2, 3], 4)


print(p.cycle_decomp)

p = ColBraid([2, 3, -2, 3, 1, 2, 3], 4, [0, 1, 2])
col_list = [0, 1, 2]
col_signs = [1, 1, 1]


print("Braid", p.braid)
print(p.cyc_by_color)
print(p.vertices)
print(p.init_vert_perm)


print("\nChecking stuff now")
graph = p.init_graph(col_signs)
p.add_clasps_hts(graph).clean_graph()
graph.print_data()
print(graph.col_first_verts)
graph = p.make_graph([1, 1, 1])
print(graph.all_single_color_homology_bases())