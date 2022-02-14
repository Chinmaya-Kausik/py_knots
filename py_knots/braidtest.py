from braid import *

p = Braid([1, 2, 1], 3)
p = ColBraid([1, 2, 1], 3, [0, 1])
col_list = [0, 1]
col_signs = [1, 1]
print(p.cycle_decomp)


print("Braid", p.braid)
print(p.cyc_by_color)
print(p.vertices)
print(p.init_vert_perm)


print("\nChecking stuff now")
graph = p.init_graph(col_signs)
p.add_clasps_hts(graph).edges
graph.print_data()
print(p.col_first_verts)