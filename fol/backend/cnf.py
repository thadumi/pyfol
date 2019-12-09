"""
:Author: Theodor A. Dumitrescu
:Date: 06/12/19
:Version: 0.0.1
"""
from typing import List

from constant import LogicalConstant
from fol.logic import EquivalenceLogicalExpression, AndLogicalExpression, \
    OrLogicalExpression, ImplicationLogicalExpression, LogicalExpression, NotLogicalExpression, \
    UniversalQuantifier, ExistentialQualifier, Not
# Eliminate ⇔ , replacing ⇔ (α⇒β)∧(β⇒α).
from variable import LogicalVariable, variable


# noinspection PyProtectedMember
def equivalence_to_cnf(lc: EquivalenceLogicalExpression) -> AndLogicalExpression:
    if not isinstance(lc, EquivalenceLogicalExpression):
        raise ValueError

    alpha = lc._args[0]
    beta = lc._args[1]

    return (alpha >> beta) & (beta >> alpha)


# noinspection PyProtectedMember
def implication_to_cnf(lc: ImplicationLogicalExpression) -> OrLogicalExpression:
    if not isinstance(lc, ImplicationLogicalExpression):
        raise ValueError

    alpha = lc._args[0]
    beta = lc._args[1]

    return ~alpha | beta


# noinspection PyProtectedMember
def move_not_inwards(lc: LogicalExpression) -> LogicalExpression:
    if not isinstance(lc, NotLogicalExpression):
        # ground term do need to verify what's inside
        return lc

    not_arg: LogicalExpression = lc._args[0]
    not_arg_type = type(not_arg)

    if not_arg_type == UniversalQuantifier:
        not_arg: UniversalQuantifier

        return ExistentialQualifier(not_arg.variables, move_not_inwards(not_arg.proposition.negated()))

    if not_arg_type == ExistentialQualifier:
        not_arg: ExistentialQualifier

        return UniversalQuantifier(not_arg._vars, move_not_inwards(not_arg._proposition.negated()))

    if not_arg_type == OrLogicalExpression:
        not_arg: OrLogicalExpression

        alpha = not_arg.alpha
        beta = not_arg.beta

        return move_not_inwards(Not(alpha)) & move_not_inwards(Not(beta))

    if not_arg_type == AndLogicalExpression:
        not_arg: AndLogicalExpression
        alpha = not_arg.alpha
        beta = not_arg.beta

        return move_not_inwards(Not(alpha)) | move_not_inwards(Not(beta))

    if not_arg_type == NotLogicalExpression:
        not_arg: NotLogicalExpression

        return not_arg.arg

    return lc  # ground term do need to verify what's inside


# noinspection PyProtectedMember
def replace_variable(expression: LogicalExpression, old_var: LogicalVariable, skolem_constant: LogicalConstant):
    if type(expression) is LogicalConstant:
        return expression

    if type(expression) is LogicalVariable:
        return expression if old_var is not expression else skolem_constant

    if type(expression) is NotLogicalExpression:
        return Not(replace_variable(expression._args[0], old_var, skolem_constant))

    if type(expression) is AndLogicalExpression:
        return replace_variable(expression.alpha, old_var, skolem_constant) & \
               replace_variable(expression.beta, old_var, skolem_constant)

    if type(expression) is OrLogicalExpression:
        return replace_variable(expression.alpha, old_var, skolem_constant) | \
               replace_variable(expression.beta, old_var, skolem_constant)

    if type(expression) is ImplicationLogicalExpression:
        return replace_variable(expression.alpha, old_var, skolem_constant) >> \
               replace_variable(expression.beta, old_var, skolem_constant)

    if type(expression) is EquivalenceLogicalExpression:
        return replace_variable(expression.alpha, old_var, skolem_constant) == \
               replace_variable(expression.beta, old_var, skolem_constant)


# Standardize variables apart by renaming them: each quantifier should use a different variable
def standardize_apart(lc, previous_variable=None):
    if previous_variable is None:
        previous_variable = set()

    if type(lc) is UniversalQuantifier or type(lc) is ExistentialQualifier:
        variables = set(lc.variables())
        variables_to_change = previous_variable.intersection(variables)

        new_variable_name = [variable(randomString(), static_value=var.value, constants=var.constants)
                             for var in variables_to_change]

        proposition = None  # TODO
        return UniversalQuantifier(tuple(new_variable_name + list(variables - variables_to_change)), proposition)


# noinspection PyProtectedMember
def skolemization(lc):
    if type(lc) not in [UniversalQuantifier, ExistentialQualifier]:
        return lc

    vars: List[LogicalVariable] = lc.variables
    proposition: LogicalExpression = lc.proposition
    # TODO(thadumi): check if there are free variables

    for var in vars:
        if var.is_closed_world():
            for constant in var.constants:
                replace_variable(proposition, var, constant)


def drop_universal_qualifiers(lc: LogicalExpression) -> LogicalExpression:
    pass


def randomString(stringLength=10):
    import random
    import string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


class UnboundVariableError(Exception):
    pass
