import gzip
from collections import OrderedDict, defaultdict
from enum import Enum, auto

import numpy as np
import scipy as sp

from .instance import Instance, VarType
from .log import logger


class ReadError:
    def __init__(self, filename, line):
        self.filename = filename
        self.line = line

    def __str__(self):
        return f'Read error on line {self.line} of file "{self.filename}"'


class ConsType(Enum):
    LowerBound = auto()
    UpperBound = auto()
    Equation = auto()


def default_cons_lb(cons_type):
    if cons_type == ConsType.UpperBound:
        return -np.inf
    else:
        return 0.0


def default_cons_ub(cons_type):
    if cons_type == ConsType.LowerBound:
        return np.inf
    else:
        return 0.0


class DefaultDict:
    def __init__(self, default_func):
        self.default_func = default_func
        self.data = dict()

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        return self.default_func(key)

    def __setitem__(self, key, value):
        self.data[key] = value


class State:
    def __init__(self):
        self.name = None
        self.first_obj_name = None
        self.obj_names = []
        cons_types = dict()
        self.cons_types = cons_types
        self.cons_lb = DefaultDict(lambda name: default_cons_lb(name))
        self.cons_ub = DefaultDict(lambda name: default_cons_ub(name))
        self.obj_coeffs = defaultdict(lambda: defaultdict(lambda: 0))
        self.coeffs = defaultdict(lambda: dict())
        self.rhs = defaultdict(lambda: 0)
        self.var_types = dict()
        self.lower_bounds = OrderedDict()
        self.upper_bounds = OrderedDict()
        self.is_integer = False


def parse_row(tokens, state):

    assert len(tokens) == 2

    if tokens[0] == "N":
        if state.first_obj_name is None:
            state.first_obj_name = tokens[1]
        state.obj_names.append(tokens[1])
        return

    cons_name = tokens[1]

    if tokens[0] == "E":
        state.cons_types[cons_name] = ConsType.Equation
        state.cons_lb[cons_name] = 0.0
        state.cons_ub[cons_name] = 0.0
    elif tokens[0] == "L":
        state.cons_types[cons_name] = ConsType.UpperBound
        state.cons_ub[cons_name] = 0.0
    elif tokens[0] == "G":
        state.cons_types[cons_name] = ConsType.LowerBound
        state.cons_lb[cons_name] = 0.0
    else:
        raise ValueError("Invalid row type")


def parse_col(tokens, state):
    assert len(tokens) >= 3

    if tokens[1] == "'MARKER'":
        if tokens[2] == "'INTORG'":
            state.is_integer = True
        elif tokens[2] == "'INTEND'":
            state.is_integer = False
        else:
            raise ValueError("Invalid marker type")
        return

    var_name = tokens[0]
    row_name = tokens[1]
    coeff = float(tokens[2])

    var_type = VarType.Integer if state.is_integer else VarType.Continuous

    state.var_types[var_name] = var_type

    # default bounds
    lb = 0.0

    if state.is_integer:
        ub = 1.0
    else:
        ub = np.inf

    assert state.lower_bounds.get(var_name, lb) == lb
    assert state.upper_bounds.get(var_name, ub) == ub

    state.lower_bounds[var_name] = lb
    state.upper_bounds[var_name] = ub

    if row_name in state.obj_names:
        state.obj_coeffs[row_name][var_name] = coeff

        if len(tokens) > 3:
            assert len(tokens) == 5
            row_name = tokens[3]
            coeff = float(tokens[4])
            state.coeffs[row_name][var_name] = coeff

    else:
        state.coeffs[row_name][var_name] = coeff


def parse_rhs(tokens, state):
    assert len(tokens) >= 3

    # rhs_name = tokens[0]
    cons_name = tokens[1]
    cons_val = tokens[2]

    state.rhs[cons_name] = float(cons_val)

    if len(tokens) > 3:
        assert len(tokens) == 5

        cons_name = tokens[3]
        cons_val = tokens[4]

        state.rhs[cons_name] = float(cons_val)


def parse_range(tokens, state):
    if len(tokens) != 3:
        raise ValueError("Invalid range line")

    cons_name = tokens[1]
    range_val = float(tokens[2])

    cons_type = state.cons_types[cons_name]

    if cons_type == ConsType.Equation:
        if range_val >= 0.0:
            state.cons_ub[cons_name] += range_val
        else:
            state.cons_lb[cons_name] += range_val
    elif cons_type == ConsType.LowerBound:
        rhs = state.rhs[cons_name]
        state.cons_lb[cons_name] = rhs - abs(range_val)
    elif cons_type == ConsType.UpperBound:
        lhs = state.rhs[cons_name]
        state.cons_ub[cons_name] = lhs + abs(range_val)
    else:
        raise ValueError("Invalid range line")


def parse_bound(tokens, state):

    assert len(tokens) >= 3

    # bound_name = tokens[1]
    bound_var = tokens[2]

    found_bound = True

    if tokens[0] == "BV":
        state.lower_bounds[bound_var] = 0.0
        state.upper_bounds[bound_var] = 1.0
    elif tokens[0] == "MI":
        state.lower_bounds[bound_var] = -np.inf
    elif tokens[0] == "PL":
        state.upper_bounds[bound_var] = np.inf
    elif tokens[0] == "FR":
        state.lower_bounds[bound_var] = -np.inf
        state.upper_bounds[bound_var] = np.inf
    else:
        found_bound = False

    if found_bound:
        if len(tokens) > 3:
            logger.warning("Ignoring extra tokens in bound line")
        return

    assert len(tokens) == 4
    bound_val = float(tokens[3])

    if tokens[0] in ["UP", "UI", "SC", "SI"]:
        state.lower_bounds[bound_var] = -np.inf
        state.upper_bounds[bound_var] = bound_val
    elif tokens[0] in ["LO", "LI"]:
        state.lower_bounds[bound_var] = bound_val
        state.upper_bounds[bound_var] = np.inf
    elif tokens[0] == "FX":
        state.upper_bounds[bound_var] = bound_val
        state.lower_bounds[bound_var] = bound_val
    else:
        raise ValueError("Invalid bound type")


def mps_lines(f):
    for index, line in enumerate(f, start=1):
        if line.startswith("*"):
            continue
        elif line.strip() == "":
            continue
        yield (index, line)


class Section(Enum):
    BOUNDS = auto()
    COLS = auto()
    ENDATA = auto()
    INIT = auto()
    NAME = auto()
    RHS = auto()
    RANGES = auto()
    ROWS = auto()


SectionIdentifiers = {
    "BOUNDS": Section.BOUNDS,
    "COLUMNS": Section.COLS,
    "ENDATA": Section.ENDATA,
    "NAME": Section.NAME,
    "RANGES": Section.RANGES,
    "RHS": Section.RHS,
    "ROWS": Section.ROWS,
}


def start_section(section, tokens, state):
    if section == Section.NAME:
        state.name = tokens[1]


def create_instance(state):

    var_names = set()

    for var in state.lower_bounds:
        var_names.add(var)

    for var in state.upper_bounds:
        var_names.add(var)

    for obj_coeff in state.obj_coeffs.values():
        for var in obj_coeff:
            var_names.add(var)

    var_names = sorted(list(var_names))

    var_lb = np.array([state.lower_bounds[var_name] for var_name in var_names])
    var_ub = np.array([state.upper_bounds[var_name] for var_name in var_names])

    assert (var_lb <= var_ub).all(), "Invalid variable bounds"

    if len(state.obj_names) > 1:
        logger.warning(
            "Choosing first of %d objective functions (%s)",
            len(state.obj_names),
            ", ".join(state.obj_names),
        )
    elif len(state.obj_names) == 0:
        raise ValueError("No objective functions found")

    obj_coeffs = state.obj_coeffs[state.first_obj_name]
    obj = np.array([obj_coeffs[var_name] for var_name in var_names])

    cons_names = set()

    for cons in state.coeffs:
        cons_names.add(cons)

    num_vars = len(var_names)
    num_cons = len(cons_names)

    cons_names = sorted(list(cons_names))

    cons_lb = np.array([state.cons_lb[cons_name] for cons_name in cons_names])
    cons_ub = np.array([state.cons_lb[cons_name] for cons_name in cons_names])

    assert (cons_lb <= cons_ub).all(), "Invalid constraint bounds"

    var_indices = {name: index for (index, name) in enumerate(var_names)}

    coeff_rows = []
    coeff_cols = []
    coeff_data = []

    for i, cons_name in enumerate(cons_names):
        cons_coeffs = state.coeffs[cons_name]

        cons_var_indices = []
        cons_var_values = []

        for var_name, var_value in cons_coeffs.items():
            cons_var_indices.append(var_indices[var_name])
            cons_var_values.append(var_value)

        num_coeffs = len(cons_coeffs)

        coeff_cols += cons_var_indices
        coeff_rows += [i] * num_coeffs
        coeff_data += cons_var_values

    coeffs = sp.sparse.coo_matrix(
        (coeff_data, (coeff_rows, coeff_cols)), shape=(num_cons, num_vars)
    )

    name = state.name
    var_types = state.var_types

    return Instance(name, var_lb, var_ub, var_types, obj, cons_lb, cons_ub, coeffs)


def parse_line(section, tokens, state):
    assert section is not None

    if section == Section.ROWS:
        parse_row(tokens, state)
    elif section == Section.COLS:
        parse_col(tokens, state)
    elif section == Section.RHS:
        parse_rhs(tokens, state)
    elif section == Section.BOUNDS:
        parse_bound(tokens, state)
    else:
        assert section == Section.RANGES
        parse_range(tokens, state)


def parse_mps(f, filename):
    state = State()
    section = None

    for index, line in mps_lines(f):
        try:
            tokens = line.split()
            section_ident = SectionIdentifiers.get(tokens[0], None)

            if section_ident is not None:

                if section_ident == Section.ENDATA:
                    break

                start_section(section_ident, tokens, state)
                section = section_ident
                continue

            parse_line(section, tokens, state)
        except Exception as e:
            raise ReadError(filename, line) from e
    else:
        raise ValueError(f"Encountered trailing lines after ENDATA at line {line}")

    return create_instance(state)


def read_mps(filename):
    logger.info('Reading MPS file "%s"', filename)
    if filename.endswith(".gz"):
        with gzip.open(filename, "rt") as f:
            return parse_mps(f, filename)
    else:
        with open(filename, "r") as f:
            return parse_mps(f, filename)


def main():
    import logging
    import sys

    logging.basicConfig(level=logging.INFO)

    for filename in sys.argv[1:]:
        prog = read_mps(filename)
        num_vars = prog.num_vars
        num_cons = prog.num_cons
        logger.info(
            "Read in instance with %d variables and %d constraints",
            num_vars,
            num_cons,
        )


if __name__ == "__main__":
    main()
