from sgraph import *
from braid import *
from typing import List, Tuple, Callable, Dict


def link_info(braid: str) -> Braid:
    start = braid.index('{')+1
    strands = int(braid[start])
    new_braid = braid[start:]
    braid1 = new_braid[new_braid.index('{')+1: new_braid.index('}')].split(',')
    braid1 = list(map(lambda x: int(x), braid1))
    return Braid(braid1, strands)


def link_info_col(braid: str, col_list: List[int]) -> ColBraid:
    start = braid.index('{')+1
    strands = int(braid[start])
    new_braid = braid[start:]
    braid1 = new_braid[new_braid.index('{')+1: new_braid.index('}')].split(',')
    braid1 = list(map(lambda x: int(x), braid1))
    return ColBraid(braid1, strands, col_list)