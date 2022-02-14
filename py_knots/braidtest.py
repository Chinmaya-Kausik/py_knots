from braid import *

p = Braid([1, 2, 1, 2, 1], 3)
col_list = [0, 1]
col_signs = [1, 1]
print(p.cycle_decomp)


print("Braid", p.braid)
print(p.cyc_by_color(col_list))
print(p.gen_vertices(col_list))
print(p.init_vert_perm(col_list))


print("\nChecking stuff now")
graph = p.init_graph(col_list, col_signs)
p.add_clasps_hts(col_list, graph).edges
graph.print_data()
print(p.col_first_verts(col_list))