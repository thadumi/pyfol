"""
:Author: thadumi
:Date: Dec 06, 2019
:Version: 0.0.1
"""


class LogicalComputation(object):
    def __init__(self, args):
        self._args = args or ()

    def _compute(self, *args):
        raise Exception(self.__class__.__name__ + ' needs to define the _compute method')

    def and_(self, other):
        return self.__and__(other)

    def _and_(self, other):
        return self.__and__(other)

    def __and__(self, other):
        return AndLogicalComputation(args=(self, other))

    def or_(self, other):
        return self.__or__(other)

    def _or_(self, other):
        return self.__or__(other)

    def __or__(self, other):
        return OrLogicalComputation(args=(self, other))

    def negated(self):
        return self.__invert__()

    def not_(self):
        return self.__invert__()

    def __invert__(self):
        return NotLogicalComputation(args=(self,))

    def __rshift__(self, other):
        return ImpliesLogicalComputation(args=(self, other))

    def __eq__(self, other):
        # WARN overriding __eq__ could cause issues on dictionaries
        return EquivalenceLogicalComputation(args=(self, other))

    def __hash__(self):
        # needed by tf.function for hashing the self argument in logical predicate name
        # WARN maybe should be considered a better hash value (?)
        return hash(str(self))


# TODO(thadumi): AND should be a monadic type and return itself during an AND operation
# ie AndLC.and(LC) -> AndLC has a new argument which is LC
# the same of OR
# this could be done via __rand__ (the operations are aggregated from lest to right)
class AndLogicalComputation(LogicalComputation):
    def __init__(self, args):
        super(AndLogicalComputation, self).__init__(args)

    def __str__(self):
        return ' ∧ '.join([str(arg) for arg in self._args])


class OrLogicalComputation(LogicalComputation):
    def __init__(self, args):
        super(OrLogicalComputation, self).__init__(args)

    def __str__(self):
        return ' ∨ '.join([str(arg) for arg in self._args])


class NotLogicalComputation(LogicalComputation):
    def __init__(self, args):
        super(NotLogicalComputation, self).__init__(args)

    def __str__(self):
        return '¬' + str(self._args[0])


class ImpliesLogicalComputation(LogicalComputation):
    def __init__(self, args):
        super(ImpliesLogicalComputation, self).__init__(args)

    def __str__(self):
        return str(self._args[0]) + ' ⇒ ' + str(self._args[1])


class EquivalenceLogicalComputation(LogicalComputation):
    def __init__(self, args):
        super(EquivalenceLogicalComputation, self).__init__(args)

    def __str__(self):
        return str(self._args[0]) + ' ⇔ ' + str(self._args[1])


class ForAllLogicalComputation(LogicalComputation):
    def __init__(self, variables, proposition):
        super(ForAllLogicalComputation, self).__init__(args=[*variables, proposition])
        self._vars = variables
        self._proposition = proposition

    def __str__(self):
        return '∀ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


class ExistsLogicalComputation(LogicalComputation):
    def __init__(self, variables, proposition):
        super(ExistsLogicalComputation, self).__init__(args=[*variables, proposition])
        self._vars = variables
        self._proposition = proposition

    def __str__(self):
        return '∃ ' + ','.join([str(var) for var in self._vars]) + ': ' + str(self._proposition)


def Not(lc: LogicalComputation) -> LogicalComputation:
    return lc.negated()


def And(arg1: LogicalComputation, arg2: LogicalComputation) -> LogicalComputation:
    return arg1.and_(arg2)


def Or(arg1: LogicalComputation, arg2: LogicalComputation) -> LogicalComputation:
    return arg1.or_(arg2)


def Implies(arg1, arg2):
    return arg1 >> arg2


def Equiv(arg1, arg2):
    return arg1 == arg2


def Forall(variables, proposition: LogicalComputation):
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

    return ForAllLogicalComputation(variables, proposition)


def Exists(variables, proposition):
    # TODO(thadumi) add doc for Exist functional API

    if type(variables) is not list or type(variables) is not tuple:
        variables = (variables,)

    return ExistsLogicalComputation(variables, proposition)
