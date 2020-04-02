#!/usr/bin/env python3
#
# abstractions.py
#
# Implements abstractions over memory using value abstractions.
#
# Author: Sreepathi Pai
#
# Written for CSC2/455 Spring 2020
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to abstractions.py. This
# work is published from: United States.

from dom_intervals import IntervalsDomain, IntervalPoint
from dom_signs import SignsDomain
import logging

logger = logging.getLogger(__name__)

class NonRelationalAbstraction(object):
    def __init__(self, domain):
        self.dom = domain

    # construct an abstraction for a set of memories
    def phi(self, M):
        m_accum = {}

        for m in M:
            m_abs = {}
            for x in m:
                m_abs[x] = self.dom.phi(m[x])

            if len(m_accum) == 0:
                m_accum = m_abs
            else:
                m_accum = self.union(m_accum, m_abs)


        # also construct BOT
        self.BOT = {}
        for x in m_accum:
            self.BOT[x] = self.dom.BOT

        return m_accum

    def lte(self, M0_abs, M1_abs):
        for x in M0_abs:
            if not self.dom.lte(M0_abs[x], M1_abs[x]): return False

        return True

    def union(self, m0, m1):
        m = {}
        for x in m0:
            m[x] = self.dom.lub(m0[x], m1[x])
            logger.debug(f"union: {m0[x]} U {m1[x]} = {m[x]}")

        return m

    def widen(self, m0, m1):
        m = {}
        for x in m0:
            m[x] = self.dom.widen(m0[x], m1[x])

        return m

    # convenience function
    def included(self, M_conc, M_abs):
        M_c_abs = self.phi(M_conc)
        return self.lte(M_c_abs, M_abs)


def test_NonRelationalAbstraction():
    nra = NonRelationalAbstraction(IntervalsDomain())

    M = [{'x': 25, 'y': 7, 'z': -12},
         {'x': 28, 'y': -7, 'z': -11},
         {'x': 20, 'y': 0, 'z': -10},
         {'x': 35, 'y': 8, 'z': -9}]

    print(nra.phi(M))


if __name__ == "__main__":
    test_NonRelationalAbstraction()

