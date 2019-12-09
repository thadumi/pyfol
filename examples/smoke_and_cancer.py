"""
:Author: Theodor A. Dumitrescu
:Date: Dec 06, 2019
:Version: 0.0.1
"""
import logging

import fol.fol_status as FOL
from fol.constant import constant
from fol.logic import Forall, Not
from fol.predicate import predicate
from fol.variable import variable

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    level=logging.DEBUG)


size = 20

friends = [('a', 'b'), ('a', 'e'), ('a', 'f'), ('a', 'g'), ('b', 'c'), ('c', 'd'), ('e', 'f'), ('g', 'h'),
           ('i', 'j'), ('j', 'm'), ('k', 'l'), ('m', 'n')]
smokes = ['a', 'e', 'f', 'g', 'j', 'n']
cancer = ['a', 'e']

g1 = {l: constant(l) for l in 'abcdefgh'}
g2 = {l: constant(l) for l in 'ijklmn'}
g = {**g1, **g2}

Friends = predicate('Friends', 2)
Smokes = predicate('Smokes', 1)
Cancer = predicate('Cancer', 1)

p = variable('p', constants=tuple(g.values()))
q = variable('q', constants=tuple(g.values()))
p1 = variable('p1', constants=tuple(g1.values()))
q1 = variable('q1', constants=tuple(g1.values()))
p2 = variable('p2', constants=tuple(g2.values()))
q2 = variable('q2', constants=tuple(g2.values()))

for (x, y) in friends:
    FOL.tell(Friends(g[x], g[y]))

for x in g1:
    for y in g1:
        if (x, y) not in friends and x < y:
            FOL.tell(Not(Friends(g[x], g[y])))

for x in g2:
    for y in g2:
        if (x, y) not in friends and x < y:
            FOL.tell(Not(Friends(g[x], g[y])))

for x in smokes:
    FOL.tell(Smokes(g[x]))

for x in g:
    if x not in smokes:
        FOL.tell(Not(Smokes(g[x])))

for x in cancer:
    FOL.tell(Cancer(g[x]))

for x in g1:
    if x not in cancer:
        FOL.tell(Cancer(g[x]).negated())
FOL.tell(Forall(p, Not(Friends(p, p))))

FOL.tell(Forall((p, q), Friends(p, q) == Friends(q, p)))
FOL.tell(Forall(p1, Smokes(p1) >> Cancer(p1)) == Forall(p2, Smokes(p2) >> Cancer(p2)))
FOL.tell(Forall(p1, Cancer(p1) >> Smokes(p1)) == Forall(p2, Cancer(p2) >> Smokes(p2)))

for axiom in FOL.AXIOMS:
    print(axiom)
