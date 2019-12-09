import unittest

from fol.constant import constant
from fol.logic import *
from fol.variable import variable


class NegationNormalForm(unittest.TestCase):

    def test_not_symbol(self):
        a = constant('A')
        john = variable('john', constants=(a,))
        self.assertEqual(Not(a).to_nnf().__str__(), Not(a).__str__())
        self.assertEqual(Not(john).to_nnf().__str__(), Not(john).__str__())

    def test_pippo(self):
        a = constant('c')
        b = constant('d')
        print(str(Not(a >> b).to_nnf()))


if __name__ == '__main__':
    unittest.main()
