import math
from typing import List, Tuple, Callable
from dataclasses import dataclass
from sgraph import *


# Custom slicing
def slice(list1, a, b):
    if(a>=b):
        return []
    else:
        return list1[a:b]


# Class for braids. Method for making spline graphs.
@dataclass(frozen=True)
class Braid:
    braid: List[int]
    strands: int

    # Finds the permutation of a braid
    def braid_to_perm(self) -> List[int]:

        # Initial identity permutation
        perm = list(range(1, self.strands+1))
        
        # Executes all transpositions
        for j in range(0, len(self.braid)):
            i = abs(self.braid[j])
            perm = slice(perm, 0, i-1) + [perm[i], perm[i-1]] + \
                            slice(perm, i+1, len(perm))

        return perm


