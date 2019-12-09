"""
:Author: thadumi
:Date: Dec 06, 2019
:Version: 0.0.2
"""

import logging

import fol.fol_status as FOL
from fol.logic import LogicalConstant


def constant(name: str) -> LogicalConstant:
    """
    TODO: add description of the constant
    :param name: the name of the constant. If the set of language constants already constantin one having the given name
                 an ValueError exception will be raised.
    :return:
    """

    if FOL.constant_already_defined(name):
        msg = '[constant] There is already a constant having the name `{}`'.format(name)
        logging.error(msg)

        raise ValueError(msg)

    config = {'name': name}
    logging.debug('Defined a new constant {}'.format(config))

    logical_constant = LogicalConstant(**config)

    FOL.track_constant(name, logical_constant)
    return logical_constant
