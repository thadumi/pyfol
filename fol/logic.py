"""
:Author: thadumi
:Date: Dec 09, 2019
:Version: 0.0.3
"""
# for https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

from typing import Tuple, Any, List


class Logic(object):
    def and_(self, other: Logic) -> AndLogicalExpression:
        return self.__and__(other)

    def _and_(self, other: Logic) -> AndLogicalExpression:
        return self.__and__(other)

    def __and__(self, other: Logic) -> AndLogicalExpression:
        return AndLogicalExpression(self, other)

    def or_(self, other: Logic) -> OrLogicalExpression:
        return self.__or__(other)

    def _or_(self, other: Logic) -> OrLogicalExpression:
        return self.__or__(other)

    def __or__(self, other: Logic) -> OrLogicalExpression:
        return OrLogicalExpression(self, other)

    def negated(self) -> NotLogicalExpression:
        return self.__invert__()

    def not_(self) -> NotLogicalExpression:
        return self.__invert__()

    def __invert__(self) -> NotLogicalExpression:
        return NotLogicalExpression(self)

    def __rshift__(self, other: Logic) -> ImplicationLogicalExpression:
        return ImplicationLogicalExpression(self, other)

    def __eq__(self, other: Logic) -> EquivalenceLogicalExpression:
        # WARN overriding __eq__ could cause issues on dictionaries
        return EquivalenceLogicalExpression(self, other)

    def __hash__(self):
        # needed by tf.function for hashing the self argument in logical predicate name
        # WARN maybe should be considered a better hash value (?)
        return hash(str(self))


class LogicalTerm(Logic):
    def __init__(self, name: str):
        super(LogicalTerm, self).__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name


class LogicalConstant(LogicalTerm):
    def __init__(self, name: str):
        if ' ' in name:
            raise ValueError('The symbolic name of a constant has to be a single word starting with an upper letter'
                             'e.g. A | A1 | AB12 | John | ....')
        super(LogicalConstant, self).__init__(name.title())


class LogicalVariable(LogicalTerm):
    def __init__(self,
                 name: str,
                 static_value: Any = None,
                 constants: List[LogicalConstant] = None):
        super(LogicalVariable, self).__init__(name)

        self._value: Any = static_value

        self._close_world: bool = constants is not None
        self._constants: List[LogicalConstant] = constants

    @property
    def is_closed_world(self):
        return self._close_world


class LogicalExpression(Logic):
    def __init__(self, args: Tuple):
        self._args: Tuple[LogicalExpression, ...] = args or ()

    def as_cnf(self):
        raise Exception(self.__class__.__name__ + 'needs to define the CNF')


class UnitaryLogicalExpression(LogicalExpression):
    def __init__(self, arg: Logic):
        super(UnitaryLogicalExpression, self).__init__(args=(arg,))

    @property
    def arg(self):
        return self._args[0]


class BinaryLogicalExpression(LogicalExpression):
    def __init__(self,
                 alpha: Logic,
                 beta: Logic):
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
    def __init__(self, alpha: Logic, beta: Logic):
        super(AndLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return ' ∧ '.join([str(arg) for arg in self._args])


class OrLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: Logic, beta: Logic):
        super(OrLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return ' ∨ '.join([str(arg) for arg in self._args])


class NotLogicalExpression(UnitaryLogicalExpression):
    def __init__(self, arg: Logic):
        super(NotLogicalExpression, self).__init__(arg)

    def __str__(self):
        return '¬' + str(self._args[0])


class ImplicationLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: Logic, beta: Logic):
        super(ImplicationLogicalExpression, self).__init__(alpha, beta)

    def __str__(self):
        return str(self._args[0]) + ' ⇒ ' + str(self._args[1])


class EquivalenceLogicalExpression(BinaryLogicalExpression):
    def __init__(self, alpha: Logic, beta: Logic):
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


class LogicalQualifier(UnitaryLogicalExpression):
    def __init__(self, variables: Tuple[LogicalVariable, ...], proposition: LogicalExpression):
        super(LogicalQualifier, self).__init__(proposition)
        self._vars: Tuple[LogicalVariable, ...] = variables
        self._proposition: LogicalExpression = proposition

    @property
    def variables(self) -> Tuple[LogicalVariable, ...]:
        return tuple(self._vars)

    @property
    def proposition(self) -> LogicalExpression:
        return self._proposition


class UniversalQuantifier(LogicalQualifier):
    def __init__(self, variables: Tuple[LogicalVariable, ...], proposition: LogicalExpression):
        super(UniversalQuantifier, self).__init__(variables, proposition)

    def __str__(self):
        return '∀ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


class ExistentialQualifier(LogicalQualifier):
    def __init__(self, variables: Tuple[LogicalVariable, ...], proposition: LogicalExpression):
        super(ExistentialQualifier, self).__init__(variables, proposition)

    def __str__(self):
        return '∃ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


def Not(lc: Logic) -> LogicalExpression:
    return lc.negated()


def And(arg1: Logic, arg2: Logic) -> LogicalExpression:
    return arg1.and_(arg2)


def Or(arg1: Logic, arg2: Logic) -> LogicalExpression:
    return arg1.or_(arg2)


def Implies(arg1: Logic, arg2: Logic) -> ImplicationLogicalExpression:
    return arg1 >> arg2


def Equiv(arg1, arg2):
    return arg1 == arg2


def Forall(variables, proposition: LogicalExpression) -> UniversalQuantifier:
    # TODO(thadumi) add doc for Forall functional API

    if type(variables) is not list and type(variables) is not tuple:
        variables = (variables,)

    if type(variables) is list:
        variables = tuple(variables)

    '''    if isinstance(proposition, LogicalComputation) \
                and not(isinstance(proposition, LogicalVariable) or isinstance(proposition, LogicalConstant)):
            raise ValueError('Expected proposition to be a LogicalComputation regardless '
                             'LogicalVariable and LogicalConstant, but received {}'.format(proposition))
    
        if any(filter(lambda type: not isinstance(type, LogicalVariable), variables)):
            raise ValueError('Founded a non instance of LogicalVariable in {}'.format(variables))
    '''

    return UniversalQuantifier(variables, proposition)


def Exists(variables, proposition: LogicalExpression) -> ExistentialQualifier:
    # TODO(thadumi) add doc for Exist functional API

    if type(variables) is not list or type(variables) is not tuple:
        variables = (variables,)

    return ExistentialQualifier(variables, proposition)
