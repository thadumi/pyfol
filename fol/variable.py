"""
:Author: Theodor A. Dumitrescu
:Date: Dec 06, 2019
:Version: 0.0.2
"""

import logging
from typing import List, Any

import fol.fol_status as FOL
from fol.constant import LogicalConstant
from fol.logic import LogicalExpression


# TODO(thadumi): a closed word variable should be implemented as an iterable
class LogicalVariable(LogicalExpression):

    def __init__(self,
                 name: str = None,
                 static_value: Any = None,
                 constants: List[LogicalConstant] = None):
        super(LogicalVariable, self).__init__(())
        self.name: str = name
        self.value: Any = static_value

        self.closed_world: bool = constants is not None
        self.constants: List[LogicalConstant] = constants

        if self.closed_world:
            self._args = constants
        else:  # static value is provided but... to think about it
            self.value = static_value

    def is_closed_world(self) -> bool:
        return self.closed_world

    def __str__(self):
        return self.name


def variable(name: str, static_value: Any = None, constants: List[LogicalConstant] = None) -> LogicalVariable:
    if FOL.variable_already_defined(name):
        msg = '[variable] There is already a variable having the name `{}`'.format(name)
        logging.error(msg)

        raise ValueError(msg)

    var = LogicalVariable(name=name, static_value=static_value, constants=constants)
    FOL.track_variable(name, var)

    return var
