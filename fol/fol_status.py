"""
:Date: Dec 06, 2019
:Version: 0.0.1
"""
from typing import Any

# NOTE(thadumi) should be this be weakref.WeakKeyDictionary references?
# if so the user should take care of hard referencing every predicate and axiom
CONSTANTS = {}
PREDICATES = {}
VARIABLES = {}
FUNCTIONS = {}  # NOTE(thadumi): useless a function is a predicate with one arg

# TODO(thadumi) define an hash method for LogicalComputation for checking that there are no others axiom already defined
AXIOMS = []


def track_constant(constant_name, meta):
    CONSTANTS[constant_name] = meta


def constant_already_defined(name: str) -> bool:
    return name in CONSTANTS.keys()


def track_predicate(predicate_name, meta):
    PREDICATES[predicate_name] = meta


def predicate_already_defined(name: str) -> bool:
    return name in PREDICATES.keys()


def track_variable(name: str, meta: Any):
    VARIABLES[name] = meta


def variable_already_defined(name: str) -> bool:
    return name in VARIABLES.keys()


def tell(lc):
    AXIOMS.append(lc)


def ask(lc):
    raise Exception  # TODO
