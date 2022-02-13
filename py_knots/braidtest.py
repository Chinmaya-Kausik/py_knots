from braid import *

p = Braid([1, 2, 1], 3)
a = p.braid_to_perm
b = p.cycle_decomp
r = p.braid
r = [1, 2, 2]
print(p.braid)
print(p.gen_vertices([0, 1]))
print(a, b)