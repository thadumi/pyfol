"""
:Author: thadumi
:Date: Dec 06, 2019
:Version: 0.0.2
"""
# for https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

from typing import Tuple


class LogicalExpression(object):
    def __init__(self, args: Tuple):
        self._args: Tuple[LogicalExpression, ...] = args or ()

    def _compute(self, *args):
        raise Exception(self.__class__.__name__ + ' needs to define the _compute method')

    def as_cnf(self):
        raise Exception(self.__class__.__name__ + 'needs to define the CNF')

    def and_(self, other: LogicalExpression) -> AndLogicalExpression:
        return self.__and__(other)

    def _and_(self, other: LogicalExpression) -> AndLogicalExpression:
        return self.__and__(other)

    def __and__(self, other: LogicalExpression) -> AndLogicalExpression:
        return AndLogicalExpression(self, other)

    def or_(self, other: LogicalExpression) -> OrLogicalExpression:
        return self.__or__(other)

    def _or_(self, other: LogicalExpression) -> OrLogicalExpression:
        return self.__or__(other)

    def __or__(self, other: LogicalExpression) -> OrLogicalExpression:
        return OrLogicalExpression(self, other)

    def negated(self) -> NotLogicalExpression:
        return self.__invert__()

    def not_(self) -> NotLogicalExpression:
        return self.__invert__()

    def __invert__(self) -> NotLogicalExpression:
        return NotLogicalExpression(self)

    def __rshift__(self, other: LogicalExpression) -> ImplicationLogicalExpression:
        return ImplicationLogicalExpression(self, other)

    def __eq__(self, other: LogicalExpression) -> EquivalenceLogicalExpression:
        # WARN overriding __eq__ could cause issues on dictionaries
        return EquivalenceLogicalExpression(self, other)

    def __hash__(self):
        # needed by tf.function for hashing the self argument in logical predicate name
        # WARN maybe should be considered a better hash value (?)
        return hash(str(self))


class UnitaryLogicalExpression(LogicalExpression):
    def __init__(self, arg: LogicalExpression):
        super(UnitaryLogicalExpression, self).__init__(args=(arg,))

    @property
    def arg(self):
        return self._args[0]


class BinaryLogicalExpression(LogicalExpression):
    def __init__(self,
                 alpha: LogicalExpression,
                 beta: LogicalExpression):
        super(BinaryLogicalExpression, self).__init__(args=(alpha, beta))

    @property
    def alpha(self):
        return self._args[0]

    @property
    def beta(self):
        return self._args[1]


# TODO(thadumi): AND should be a monadic type and return itself during an AND operation
# ie AndLC.and(LC) -> AndLC has a new argument which is LC
# the same of OR
# this could be done via __rand__ (the operations are aggregated from lest to right)
class AndLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: LogicalExpression, beta: LogicalExpression):
        super(AndLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return ' ∧ '.join([str(arg) for arg in self._args])


class OrLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: LogicalExpression, beta: LogicalExpression):
        super(OrLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return ' ∨ '.join([str(arg) for arg in self._args])


class NotLogicalExpression(UnitaryLogicalExpression):
    def __init__(self, arg: LogicalExpression):
        super(NotLogicalExpression, self).__init__(arg)

    def __str__(self):
        return '¬' + str(self._args[0])


class ImplicationLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: LogicalExpression, beta: LogicalExpression):
        super(ImplicationLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return str(self._args[0]) + ' ⇒ ' + str(self._args[1])


class EquivalenceLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: LogicalExpression, beta: LogicalExpression):
        super(EquivalenceLogicalExpression, self).__init__(alpha, beta)

    def as_cnf(self, first_step=False):
        """
        from α⇔β to (α⇒β)∧(β⇒α)
        :param first_step:
        :return: (α⇒β)∧(β⇒α) if first_step is True otherwise ¬α∨β ∧ ¬β∨α
        """
        alpha = self._args[0]
        beta = self._args[1]

        if first_step:
            return (alpha >> beta) & (beta >> alpha)
        else:
            return (alpha >> beta).as_cnf() & (beta >> alpha).as_cnf()

    def __str__(self):
        return str(self._args[0]) + ' ⇔ ' + str(self._args[1])


class ForAllLogicalExpression(LogicalExpression):
    def __init__(self, variables, proposition: LogicalExpression):
        super(ForAllLogicalExpression, self).__init__(args=tuple([*variables, proposition]))
        self._vars = variables
        self._proposition = proposition

    # TODO(thadumi) as_cnf

    @property
    def variables(self):
        return self._vars

    @property
    def proposition(self) -> LogicalExpression:
        return self._proposition

    def __str__(self):
        return '∀ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


class ExistsLogicalExpression(LogicalExpression):
    def __init__(self, variables, proposition: LogicalExpression):
        super(ExistsLogicalExpression, self).__init__(args=tuple([*variables, proposition]))
        self._vars = variables
        self._proposition = proposition

    @property
    def variables(self):
        return self._vars

    @property
    def proposition(self) -> LogicalExpression:
        return self._proposition

    def __str__(self):
        return '∃ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


def Not(lc: LogicalExpression) -> LogicalExpression:
    return lc.negated()


def And(arg1: LogicalExpression, arg2: LogicalExpression) -> LogicalExpression:
    return arg1.and_(arg2)


def Or(arg1: LogicalExpression, arg2: LogicalExpression) -> LogicalExpression:
    return arg1.or_(arg2)


def Implies(arg1: LogicalExpression, arg2: LogicalExpression) -> ImplicationLogicalExpression:
    return arg1 >> arg2


def Equiv(arg1, arg2):
    return arg1 == arg2


def Forall(variables, proposition: LogicalExpression) -> ForAllLogicalExpression:
    # TODO(thadumi) add doc for Forall functional API

    if type(variables) is not list and type(variables) is not tuple:
        variables = (variables,)

    '''    if isinstance(proposition, LogicalComputation) \
                and not(isinstance(proposition, LogicalVariable) or isinstance(proposition, LogicalConstant)):
            raise ValueError('Expected proposition to be a LogicalComputation regardless '
                             'LogicalVariable and LogicalConstant, but received {}'.format(proposition))
    
        if any(filter(lambda type: not isinstance(type, LogicalVariable), variables)):
            raise ValueError('Founded a non instance of LogicalVariable in {}'.format(variables))
    '''

    return ForAllLogicalExpression(variables, proposition)


def Exists(variables, proposition: LogicalExpression) -> LogicalExpression:
    # TODO(thadumi) add doc for Exist functional API

    if type(variables) is not list or type(variables) is not tuple:
        variables = (variables,)

    return ExistsLogicalExpression(variables, proposition)
