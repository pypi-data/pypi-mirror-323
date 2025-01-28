from enum import Enum, auto

import scipy as sp


class VarType(Enum):
    Integer = auto()
    Continuous = auto()


class Instance:
    def __init__(self, name, var_lb, var_ub, var_types, obj, cons_lb, cons_ub, coeffs):

        self.name = name
        (self.num_cons, self.num_vars) = coeffs.shape

        assert var_lb.shape == (self.num_vars,)
        assert var_ub.shape == (self.num_vars,)
        assert obj.shape == (self.num_vars,)

        assert len(var_types) == self.num_vars

        assert cons_lb.shape == (self.num_cons,)
        assert cons_ub.shape == (self.num_cons,)

        assert sp.sparse.issparse(coeffs)

        self.var_lb = var_lb
        self.var_ub = var_ub
        self.var_type = var_types
        self.obj = obj
        self.cons_lb = cons_lb
        self.cons_ub = cons_ub
        self.coeffs = coeffs

    def __str__(self):
        return (
            f"Instance with {self.num_vars} variables and {self.num_cons} constraints"
        )
