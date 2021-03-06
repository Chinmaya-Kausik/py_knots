import math
from typing import List, Tuple, Callable, Dict, Set
from functools import cached_property
from dataclasses import dataclass
from copy import deepcopy

"""
----- Generates the homology basis for a spline graph and
----- computes generalized Seifert matrices. 
----- The presentation matrix is computed in pres_mat.py. 
"""


# Finds a minimum spanning tree for a graph
# Returns the set and dictionary describing the edges of the MST
def find_mst(verti: Set, edges_col: Set, edge_dict: Dict):

    mst_edges = set()
    mst_vertices = {0}
    mst_dict = dict()

    vertices_remaining = verti.difference(mst_vertices)

    for v in verti:
        mst_dict[v] = set()

    explored = [0]
    queue = [0]

    while(queue):
        node = queue.pop(0)
        for v in edge_dict[node]:
            if(v not in explored):
                queue.append(v)
                explored.append(v)
                if(node>v):
                    mst_edges.add((v, node))
                else:
                    mst_edges.add((node, v))
                mst_dict[v].add(node)
                mst_dict[node].add(v)

    return mst_edges, mst_dict


# Finds the shortest path from the vertex init to the vertex term
# Using a breadth first search
def find_path(verti: Set, edges_col: Set, edge_dict: Dict,
        init: int, term: int) -> List[int]:

    explored = [init]
    queue = [[init]]

    while(queue):
        path = queue.pop(0)
        node = path[-1]
        for v in edge_dict[node]:
            if(v not in explored):
                if(v == term):
                    return path+[v]
                else:
                    queue.append(path +[v])
                explored.append(v)


# Class for vertices
@dataclass(frozen=True, repr=False)
class SVertex:
    num: int
    col: int

    def __repr__(self):
        return "V({}, {})".format(self.num, self.col)


# Class for edges
@dataclass(frozen=True, repr=False)
class SEdge:
    initial: SVertex
    terminal: SVertex
    num: int
    typ: int
    col: int

    def __repr__(self):
        return "E({}, {}, {}, {}, {})".format(self.initial,
            self.terminal, self.num, self.typ, self.col)


# Class for oriented edges
@dataclass(repr=False, init=False)
class OEdge():
    sign: int

    def __init__(self, edge: SEdge, sign: int):
        self.initial = edge.initial
        self.terminal = edge.terminal

        self.num = edge.num
        self.typ = edge.typ
        self.col = edge.col
        self.sign = sign

    def __repr__(self):
        return "OE({}, {}, {}, {}, {}, {})".format(self.initial,
            self.terminal, self.num, self.typ, self.col, self.sign)

    # The true initial vertex, accounting for orientation.
    @cached_property
    def true_initial(self) -> SVertex:
        if(self.sign == 1):
            return self.initial
        else:
            return self.terminal

    # The true terminal vertex, accounting for orientation.
    @cached_property
    def true_terminal(self) -> SVertex:
        if(self.sign == 1):
            return self.terminal
        else:
            return self.initial

    # Returns the SEdge corresponding to an oriented edge
    @cached_property
    def edge(self):
        return SEdge(self.initial, self.terminal, self.num, self.typ, self.col)


# Checks if a list of edges forms a loop.
def check_loop(lst: List[OEdge]) -> bool:
    is_loop = True 
    for i in range(len(lst)-1):
        is_loop = is_loop and (lst[i].true_terminal == lst[i+1].true_initial)

    return is_loop and (lst[-1].true_terminal == lst[0].true_initial)


# Class for loops in spline graphs.
@dataclass
class Loop:
    edges: List[OEdge]

    def __post_init__(self):
        assert check_loop(self.edges), "This list does not form a loop: "\
            +str(self.edges)


# Class for spline graphs of clasp complexes
@dataclass
class SGraph:
    vert: List[SVertex]
    edges: List[SEdge]
    vve: Dict[Tuple[SVertex, SVertex], List[SEdge]]
    ve: Dict[SVertex, List[SEdge]]
    colors: int
    col_signs: List[int]

    """

    ------- Tools for making the final spline graph ------

    """

    # Add a new edge to the front of the graph.
    def add_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = self.vve[(init, term)] + [new_edge]
        self.ve[init] = self.ve[init] + [new_edge]
        self.ve[term] = self.ve[term] + [new_edge]

    # Add a new edge to the back of the graph.
    def add_init_edge(self, init: SVertex, term: SVertex,
                 typ: int, col: int):
    
        new_edge = SEdge(init, term, len(self.vve[(init, term)]), typ, col)

        self.edges += [new_edge]
        self.vve[(init, term)] = [new_edge] + self.vve[(init, term)]
        self.ve[init] = [new_edge] + self.ve[init]
        self.ve[term] = [new_edge] + self.ve[term]

    # Deletes an edge from the graph
    def delete_edge(self, edge: SEdge):
        self.edges.remove(edge)
        self.vve[(edge.initial, edge.terminal)].remove(edge)
        self.ve[edge.initial].remove(edge)
        self.ve[edge.terminal].remove(edge)

    # Finds and deletes a redundant pair of edges in the graph
    def delete_redundant_pair(self) -> bool:
        exists = False
        for i1 in range(len(self.vert)):
            for i2 in range(i1+1, len(self.vert)):
                v1 = self.vert[i1]
                v2 = self.vert[i2]
                vv_edges = self.vve[(v1, v2)]
                v1_edges = self.ve[v1]
                v2_edges = self.ve[v2]
                for j in range(len(vv_edges)-1):
                    edge1 = vv_edges[j]
                    edge2 = vv_edges[j+1]
                    if((edge1.typ == -edge2.typ) and
                        (v2_edges.index(edge2) == v2_edges.index(edge1)+1)
                    and (v1_edges.index(edge2) == v1_edges.index(edge1)+1)):
                        self.delete_edge(edge1)
                        self.delete_edge(edge2)
                        exists = True
                        return exists
                if(len(vv_edges)>=2):
                    edge1 = vv_edges[-1]
                    edge2 = vv_edges[0]
                    if((edge1.typ == -edge2.typ) and
                        (v2_edges.index(edge2) == v2_edges.index(edge1)+1)
                    and (v1_edges.index(edge2) == v1_edges.index(edge1)+1)):
                        self.delete_edge(edge1)
                        self.delete_edge(edge2)
                        exists = True
                        return exists

        return exists

    # Cleans up redundant pairs of edges.
    def clean_graph(self):
        exists = True
        while(exists):
            exists = self.delete_redundant_pair()

    # Prints the abstract data of the graph
    # List of vertex indices, then edges = (init, term, type)
    def print_data(self):
        print("Vertices:", list(range(len(self.vert))))
        print("Colors:", list(map(lambda x: x.col, self.vert)))
        print("Edges: ", end='')
        for edge in self.edges:
            print("("+ str(self.vert.index(edge.initial))+ ", " +
                str(self.vert.index(edge.terminal)) + ", " +
                str(edge.typ) + "), ", end='')
        print()

    # List of the first vertices in each color.
    def col_first_verts(self) -> List[SVertex]:
        vert = self.vert
        tally = list(range(self.colors))
        col_1st_verts = []

        for v in vert:
            if(v.col in tally):
                col_1st_verts.append(v)
                tally = tally[1:]

        return col_1st_verts

    # Makes sure each Seifert surface is connected
    def colors_connected(self) -> None:
        vert = self.vert

        while(len(vert) != 1):
            v0 = vert[0]
            v1 = vert[1]
            if(v0.col == v1.col):
                if(self.vve[(v0, v1)] == []):
                    self.add_edge(v0, v1, 1, v0.col)
                    self.add_edge(v0, v1, -1, v0.col)
            vert = vert[1:]

    # Checks if two colors are connected.
    # The lower color should be the first input.
    def check_connected(self, col1: int, col2: int) -> bool:
        connected = False
        i = 0
        while((not connected) and (i<len(self.vert))):
            if(self.vert[i].col == col1):
                for v2 in self.vert:
                    if((v2.col == col2) and
                    (self.vve[(self.vert[i], v2)] != [])):
                        connected = True
                        break
            i+=1
        return connected

    # Makes sure the graph across colors is complete
    def make_complete(self):
        v_col = self.col_first_verts()
        print("v_col", v_col)
        for color1 in range(len(v_col)):
            for color2 in range(len(v_col)):
                if((color1 < color2) and
                    (self.vve[(v_col[color1], v_col[color2])] == []) and
                (not self.check_connected(color1, color2))):
                    self.add_edge(v_col[color1], v_col[color2], 2, color1)
                    self.add_edge(v_col[color1], v_col[color2], -2, color1)

    # Finds the connected component of a set
    def find_conn_comp(self, conn_comp: Set[int]):
        all_colors = list(range(self.colors))

        old_conn_comp = set()
        new_conn_comp = conn_comp

        while(old_conn_comp != new_conn_comp):
            old_conn_comp = deepcopy(new_conn_comp)
            for i in all_colors:
                if i not in old_conn_comp:
                    for col in old_conn_comp:
                        if((i<col) and self.check_connected(i, col)):
                            new_conn_comp.add(i)
                        elif((i>col) and self.check_connected(col, i)):
                            new_conn_comp.add(i)

        return new_conn_comp

    # Makes sure the graph across colors is connected
    def make_connected(self):
        conn_comp = self.find_conn_comp({0})
        want_conn = set(range(self.colors))
        v_col = self.col_first_verts()

        while(conn_comp != want_conn):

            i = min({x for x in want_conn if x not in conn_comp})

            self.add_edge(v_col[0], v_col[i], 2, 0)
            self.add_edge(v_col[0], v_col[i], -2, 0)

            conn_comp.update(self.find_conn_comp({i}))

    """

    ------ Now moving on to generating a homology basis ------

    """

    # Gives a value to a lift (or not) of a vertex.
    # If it is not lifted (lift = 0), the value is just its index.
    # Otherwise add or subtract 0.5 depending on the direction of the lift
    def value(self, vert: SVertex, lift: int, col_lifts: List[int]) -> float:
        assert vert in self.vert, "The vertex " + str(vert) + \
            " is not in the graph"

        if(lift == 0):
            return vert.num
        else:
            return vert.num +\
                self.col_signs[vert.col]*0.5*col_lifts[vert.col]

    # Finds the rightmost edge between two vertices.
    def max_edge(self, init: SVertex, term: SVertex) -> SEdge:
        return self.vve[(init, term)][-1]

    # Finds the homology basis of the subgraph
    # corresponding to a given color
    def single_color_hom_basis(self, col: int) -> List[Loop]:
        hom_basis = []
        i = self.vert.index(self.col_first_verts()[col])
        n = len(self.vert)

        while((i<n-1) and (self.vert[i+1].col == col)):
            v1 = self.vert[i]
            v2 = self.vert[i+1]
            m_edge = OEdge(self.max_edge(v1, v2), -1)
            for edge in self.vve[(v1, v2)][:-1]:
                o_edge = OEdge(edge, 1)

                hom_basis.append(Loop([o_edge, m_edge]))
            i+=1

        return hom_basis

    # Combines the homology bases for subgraphs for individual colors.
    @cached_property
    def all_single_color_hom_bases(self):
        hom_basis = []
        for col in range(self.colors):
            hom_basis += self.single_color_hom_basis(col)
        return hom_basis

    # Finds the rightmost edge connecting two colors.
    # Enter the lower color first.
    def max_connector(self, col1: int, col2: int) -> SEdge:
        for edge in reversed(self.edges):
            if((edge.initial.col, edge.terminal.col) == (col1, col2)):
                return edge

    # Connects two vertices of the same color.
    def connect_vertices(self, v1: SVertex, v2: SVertex) -> List[OEdge]:
        assert v1.col == v2.col,\
            "The vertices {} {} have different colors".format(v1, v2)

        path = []
        if(v1.num > v2.num):
            num = v1.num
            while(num>v2.num):
                vert_1 = self.vert[num]
                vert_2 = self.vert[num-1]
                path.append(OEdge(self.max_edge(vert_2, vert_1), -1))
                num -= 1
        else:
            num = v1.num
            while(num<v2.num):
                vert_1 = self.vert[num]
                vert_2 = self.vert[num+1]
                path.append(OEdge(self.max_edge(vert_1, vert_2), 1))
                num += 1

        return path

    # Completes an edge into a loop
    def make_loop(self, edge: SEdge) -> Loop:
        v1 = edge.initial
        v2 = edge.terminal
        assert v1.col != v2.col,\
            "The endpoints {} {} have the same color".format(v1, v2)
        max_conn = self.max_connector(v1.col, v2.col)
        path_1 = self.connect_vertices(v2, max_conn.terminal)
        path_2 = self.connect_vertices(max_conn.initial, v1)

        return Loop([OEdge(edge, 1)] + path_1 + [OEdge(max_conn, -1)] + path_2)

    # Finds the homology basis corresponding
    # to the local graph between two given colors.
    def local_graph_hom_basis(self, col1: int, col2: int) -> List[Loop]:
        hom_basis = []

        m_edge = self.max_connector(col1, col2)
        for edge in self.edges:
            if((edge.initial.col == col1) and (edge.terminal.col == col2) and
            (edge != m_edge)):
                hom_basis.append(self.make_loop(edge))

        return hom_basis

    # Finds and collects homology bases for all local graphs between colors.
    @cached_property
    def all_local_graph_hom_bases(self) -> List[Loop]:
        hom_basis = []

        for col1 in range(self.colors):
            for col2 in range(col1+1, self.colors):
                hom_basis += self.local_graph_hom_basis(col1, col2)

        return hom_basis

    # Converts a loop of color indices into a loop in the spline graph
    def convert_col_loop(self, col_loop: List[int]) -> Loop:
        edge_list = []

        for i in range(len(col_loop)-1):
            if(col_loop[i]>col_loop[i+1]):
                max_conn = OEdge(
                    edge=self.max_connector(col_loop[i+1], col_loop[i]),
                    sign=-1)
            else:
                max_conn = OEdge(
                    edge=self.max_connector(col_loop[i], col_loop[i+1]),
                    sign=1)

            edge_list.append(max_conn)
        path = []

        for i in range(len(edge_list)-1):
            e1 = edge_list[i]
            e2 = edge_list[i+1]

            connecting_path = self.connect_vertices(
                e1.true_terminal, e2.true_initial)

            path += [e1] + connecting_path

        e_n = edge_list[-1]
        e_1 = edge_list[0]
        connecting_path = self.connect_vertices(
            e_n.true_terminal, e_1.true_initial)

        path += [e_n] + connecting_path

        return Loop(path)

    # Finds the graph of colors
    def find_col_graph(self):
        verti = set(range(self.colors))

        edges_col = set()
        edge_dict = dict()

        for v in verti:
            edge_dict[v] = set()

        for i in verti:
            for j in range(i+1, self.colors):
                if(self.check_connected(i, j)):
                    edges_col.add((i, j))
                    edge_dict[i].add(j)
                    edge_dict[j].add(i)

        return (verti, edges_col, edge_dict)

    # Finds a homology basis for the global graph across colors
    # with no edges repeated
    @cached_property
    def global_color_graph_basis(self) -> List[Loop]:
        hom_basis = []

        verti, edges_col, edge_dict = self.find_col_graph()
        mst_edges, mst_dict = find_mst(verti, edges_col, edge_dict)

        edges_remaining = edges_col.difference(mst_edges)

        for edge in edges_remaining:
            init = edge[0]
            term = edge[1]
            path1 = find_path(verti, mst_edges, mst_dict, init, term)
            new_loop = self.convert_col_loop(path1 + [init])
            hom_basis.append(new_loop)

        return hom_basis

    # Finds the homology basis corresponding to the 
    # (possibly not complete) graph of colors.
    @cached_property
    def complete_graph_hom_basis(self) -> List[Loop]:
        hom_basis = []

        for col1 in range(self.colors):
            for col2 in range(col1+1, self.colors):
                for col3 in range(col2+1, self.colors):
                    hom_basis.append(self.convert_col_loop(
                        [col1, col2, col3, col1]))

        return hom_basis

    # Finds the homology basis for a spline graph.
    @cached_property
    def hom_basis(self):
        return self.all_single_color_hom_bases +\
            self. all_local_graph_hom_bases +\
            self.global_color_graph_basis

    # Number of single color loops.
    @cached_property
    def single_color_loops(self) -> int:
        return len(self.all_single_color_hom_bases)

    # Number of local graph loops.
    @cached_property
    def local_graph_loops(self) -> int:
        return len(self.all_local_graph_hom_bases)

    # Number of complete graph loops.
    @cached_property
    def complete_graph_loops(self) -> int:
        return len(self.complete_graph_hom_basis)

    # Computes the contribution of two oriented edges to linking.
    def edge_link(self, edge1: OEdge, edge2: OEdge,
            col_lifts: List[int]) -> int:

        u1 = edge1.initial
        u2 = edge1.terminal
        v1 = edge2.initial
        v2 = edge2.terminal

        val_u1 = self.value(u1, 1, col_lifts)
        val_u2 = self.value(u2, 1, col_lifts)
        val_v1 = self.value(v1, 0, col_lifts)
        val_v2 = self.value(v2, 0, col_lifts)

        link = 0

        if(self.edges.index(edge1.edge) < self.edges.index(edge2.edge)):
            pos = 1
        else:
            pos = 0

        if(self.col_signs[u1.col]*col_lifts[u1.col] == 1):
            up_down = 0
        else:
            up_down = 1

        if(edge1.typ>0):
            handed = 0
        else:
            handed = 1

        if((val_v1 < val_u1 < val_v2 < val_u2) or
        (val_u1 < val_v1 < val_u2 < val_v2)):
            if(edge1.edge == edge2.edge):
                link = [[1, 0], [0, -1]][up_down][handed]
            else:
                if(val_v1 < val_u1 < val_v2 < val_u2):
                    link = pos
                else:
                    link = -pos

        # print(edge1, edge2, link*edge1.sign*edge2.sign,
        #    self.edges.index(edge1.edge), self.edges.index(edge2.edge))
    
        return link*edge1.sign*edge2.sign

    # Computes the linking number of two loops.
    # The first one is lifted.
    def linking_number(self, loop_1: Loop, loop_2: Loop,
            col_lifts: List[int]) -> int:
        link = 0

        for edge1 in loop_1.edges:
            for edge2 in loop_2.edges:
                link += self.edge_link(edge1, edge2, col_lifts)

        return link

    # Computes the generalized Seifert matrix for a given lifting.
    def gen_seifert_matrix(self, col_lifts: List[int]) -> List[List[int]]:
        n = len(self.hom_basis)

        gen_seif = [list(range(n)) for i in range(n)]

        for i in range(n):
            for j in range(n):
                gen_seif[i][j] = self.linking_number(self.hom_basis[i],
                                            self.hom_basis[j], col_lifts)

        return gen_seif

    # Euler characteristic of deletions
    def euler_char(self, i: int) -> int:
        assert i < self.colors, "{} is not a color".format(i)

        graph_v = 0 
        for v in self.vert:
            if(v.col != i):
                graph_v += 1

        graph_e = 0
        for edge in self.edges:
            if((edge.initial.col != i) and (edge.terminal.col != i)):
                graph_e += 1 

        return graph_v - graph_e

    # Euler characteristic of the spline graph
    def sgraph_euler_char(self) -> int:

        graph_v = 0 
        for v in self.vert:
            graph_v += 1

        graph_e = 0
        for edge in self.edges:
            graph_e += 1 

        return graph_v - graph_e

    # The sign of the clasp complex in the sense of Cimasoni.
    # The product of the signs of clasps
    @cached_property
    def clasp_sign(self) -> int:
        sgn = 1
        for edge in self.edges:
            if(edge.typ == -2):
                sgn *= -1

        return sgn

    # The linking number of two sub-links prescribed by two colors
    # This is only used when both sub-links are knots
    # Needs the framing to determine the self linking number
    def linking_number_links(self, col1: int, col2: int,
    framing: List[int]) -> int:

        if(col1==col2):
            return framing[col1]
        elif(col1<col2):
            clasps = filter(lambda e: ((e.initial.col == col1)
                and (e.terminal.col == col2)), self.edges)
            link = 0
            for e in clasps:
                if(e.typ == 2):
                    link -= 1
                else:
                    link += 1
        else:
            link = self.linking_number_links(col2, col1, framing)

        return link

    # Returns the linking matrix of a framed colored link
    # Again, this is only used when each color has a single knot
    def linking_matrix(self, framing: List[int]):

        assert len(framing)>=self.colors, "Framing list should have {}\
         elements instead of {} elements".format(self.colors, len(framing))

        mat = [list(range(self.colors)) for i in range(self.colors)]

        for col1 in range(self.colors):
            for col2 in range(self.colors):
                mat[col1][col2] = self.linking_number_links(
                    col1, col2, framing)

        return mat
