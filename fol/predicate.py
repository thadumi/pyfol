"""
:Author: thadumi
:Date: Dec 09, 2019
:Version: 0.0.2
"""
from __future__ import annotations

import logging
from typing import Tuple

import fol.fol_status as FOL
from fol.logic import LogicalExpression, LogicalTerm


class Predicate(object):
    def __init__(self, **kwargs):
        logging.debug('[predicate] Clearing a new predicate: ' + str(kwargs))
        self.name: str = kwargs['name']
        self.number_of_arguments: int = kwargs['number_of_arguments']

    def __call__(self, *args: LogicalTerm, **kwargs) -> LogicalPredicate:
        if len(args) != self.number_of_arguments:
            raise ValueError('The predicate {} is defined with {} arguments but has been called with {} args.'
                             .format(self.name, self.number_of_arguments, len(args)))
        return LogicalPredicate(self, tuple([*args]))


class LogicalPredicate(LogicalExpression):
    def __init__(self,
                 predicate: Predicate,
                 input_terms: Tuple[LogicalTerm, ...]):
        super(LogicalPredicate, self).__init__(input_terms)
        self.predicate = predicate

    def __str__(self):
        return self.predicate.name + '(' + ', '.join([str(i) for i in self._args]) + ')'


def predicate(name: str,
              number_of_arguments: int, ) -> Predicate:
    """
    TODO(thadumi) doc for predicate
    :param name:
    :param number_of_arguments:
    :return:
    """

    if FOL.predicate_already_defined(name):
        msg = '[predicate] There is already a predicate having the name `{}`'.format(name)
        logging.error(msg)

        raise ValueError(msg)

    if number_of_arguments <= 0:
        raise ValueError('A predicate should be defined with at least one argument.')

    config = {'name': name,
              'number_of_arguments': number_of_arguments
              }

    p = Predicate(**config)
    FOL.track_predicate(name, p)
    return p
