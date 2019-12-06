"""
:Author: thadumi
:Date: Dec 06, 2019
:Version: 0.0.1
"""
import logging

import fol.fol_status as FOL
from fol.logic import LogicalComputation


class LogicalPredicate(LogicalComputation):
    def __init__(self,
                 predicate,
                 input_terms=None):
        super(LogicalPredicate, self).__init__(input_terms)
        self.predicate = predicate

    def __str__(self):
        return self.predicate.name + '(' + ', '.join([str(i) for i in self._args]) + ')'


class Predicate(object):
    def __init__(self, **kwargs):
        logging.debug('Clearing a new predicate: ' + str(kwargs))
        self.name = kwargs['name']
        self.number_of_arguments = kwargs['number_of_arguments']

    def __call__(self, *args: LogicalComputation, **kwargs) -> LogicalPredicate:
        return LogicalPredicate(self, [*args])


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
        raise ValueError

    config = {'name': name,
              'number_of_arguments': number_of_arguments
              }

    p = Predicate(**config)
    FOL.track_predicate(name, p)
    return p
