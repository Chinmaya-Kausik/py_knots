from sgraph import *
from sympy import *
from sympy.matrices import Matrix, zeros
import copy
import cmath
import numpy as np
from numpy.linalg import eigh


# Custom function to swap rows in a matrix
def swap_rows(i: int, j: int, M: Matrix) -> None:
    for ind in range(shape(M)[1]):
        a = copy.deepcopy(M[i, ind])
        M[i, ind] = -M[j, ind]
        M[j, ind] = a


# Class for presentation matrices
@dataclass(frozen=True)
class PolyMatrix:
    variables: List[Symbol]
    M: Matrix

    @cached_property
    def bareiss_det(self) -> Add:

        M = copy.deepcopy(self.M)
        variables = self.variables
        n = shape(M)[0]

        for k in range(n-1):

            if(M[k, k] == 0):
                singular = True
                for j in range(k+1, n):
                    if(M[j, k] != 0):
                        singular = False
                        swap_rows(k, j, M)
                if(singular):
                    return symbols("0")

            for i in range(k+1, n):
                for j in range(k+1, n):
                    f = M[i, j]*M[k, k] - M[i, k]*M[k, j]
                    f = Poly(f, variables)
                    if(k==0):
                        g = Poly(1, variables)
                    else:
                        g = M[k-1, k-1]
                        g = Poly(g, variables)
                    q, r = div(f, g, domain='ZZ')
                    assert r == Poly(0, variables), "Not divisible"
                    q = q.as_expr()
                    M[i, j] = q

        det = M[n-1, n-1]
        return det

    @cached_property
    def stripped_multivar_alexander_poly(self) -> Add:
        f = copy.deepcopy(self.bareiss_det)
        for var in self.variables:
            divides = True
            while(divides):
                q, r = div(f.as_poly(), var)
                if(r == Poly(0, self.variables)):
                    f = q
                else:
                    divides = False
        f = f.as_expr()
        return f

    def conway_potential_function(self, graph: SGraph) -> Add:
        M = copy.deepcopy(self.M)
        variables = copy.deepcopy(self.variables)
        f = PolyMatrix(variables, -M).bareiss_det

        for var in variables:
            f = f.subs(var, var**(-2))

        f = f*(prod(variables)**shape(self.M)[0])

        for i in range(len(variables)):
            e = variables[i]
            f = f*(e-e**(-1))**(graph.euler_char(i)-1)

        cpf = (cancel(f)*graph.clasp_sign).as_expr()
        return cpf

    def multivar_alexander_poly(self, graph: SGraph):
        cpf = self.conway_potential_function(graph)
        for var in self.variables:
            cpf = cpf.subs(var, var**(1/2))
        return cpf

    def signature(self, omega: List[complex]) -> int:
        mult = 1 
        for c in omega:
            mult *= (1-c.conjugate())
        M = copy.deepcopy(self.M)
        for i in range(len(self.variables)):
            M = M.subs(self.variables[i], omega[i])
        M = np.array(mult*M).astype(np.float64)
        eig_val, eig_vect = eigh(M)
        print(eig_val)
        sgn = 0
        for e in eig_val:
            if(e>0):
                sgn -= 1
            else:
                sgn += 1
        return sgn
 

# Computes the presentation matrix for the graph.
def presentation_matrix(graph: SGraph) -> PolyMatrix:

    pres = zeros(len(graph.hom_basis))
    variables = []

    for j in range(graph.colors):
        exec("""t{} = symbols("t{}")""".format(j, j))
        exec("variables.append(t{})".format(j), None, locals())

    for i in range(2**graph.colors):
        col_lifts = [1]*graph.colors
        mult = 1

        tally = int(i)
        for j in range(graph.colors):
            if(tally %2 == 0):
                mult = mult*variables[graph.colors-j-1]
                col_lifts[graph.colors-j-1] = -1
                tally /= 2
            else:
                tally = (tally-1)/2

        sign = prod(col_lifts)
        print(mult, col_lifts, sign)

        M = Matrix(graph.gen_seifert_matrix(col_lifts))
        print(M)
        pres = pres + M*sign*mult

    return PolyMatrix(variables, pres)




