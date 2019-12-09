"""
:Author: Theodor A. Dumitrescu
:Date: Dec 09, 2019
:Version: 0.0.3
"""

import logging
from typing import List, Any

import fol.fol_status as FOL
from fol.logic import LogicalVariable, LogicalConstant


def variable(name: str, static_value: Any = None, constants: List[LogicalConstant] = None) -> LogicalVariable:
    if FOL.variable_already_defined(name):
        msg = '[variable] There is already a variable having the name `{}`'.format(name)
        logging.error(msg)

        raise ValueError(msg)

    var = LogicalVariable(name=name, static_value=static_value, constants=constants)
    FOL.track_variable(name, var)

    return var
