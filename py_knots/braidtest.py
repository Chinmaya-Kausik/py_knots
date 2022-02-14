from braid import *

p = Braid([1, 2, 1], 3)
a = p.braid_to_perm
b = p.cycle_decomp
r = p.braid
r = [1, 2, 2]
print(p.braid)
print(p.gen_vertices([0, 1]))
print(a, b)
graph = p.init_graph([0, 1], [1, 1])
print(p.cyc_by_color([0, 1]))
print(p.gen_vertices([0, 1]))
print(p.init_vert_perm([0, 1]))
print(graph)
print(p.add_clasps_hts([0, 1], graph))