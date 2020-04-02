#!/usr/bin/env python3
#
# dom_intervals.py
#
# An implementation of the intervals value abstraction. Assumes values
# are integers.
#
# Author: Sreepathi Pai
#
# Written for CSC2/455 Spring 2020
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to
# dom_intervals.py. This work is published from: United States.
#
# Note: this is still incomplete, and should throw NotImplementedErrors
#

import logging

logger = logging.getLogger(__name__)

class IntervalPoint(object):
    PINF = "+inf"
    NINF = "-inf"

    def __init__(self, pt):
        self.pt = pt

    def __eq__(self, other):
        # this equates infinity, which should be okay
        if isinstance(other, IntervalPoint):
            return other.pt == self.pt
        else:
            raise NotImplementedError(other)

    def __lt__(self, other: 'IntervalPoint'):
        if self.pt == self.PINF:
            # +inf, -inf/F; +inf, n/F; +inf, +inf/F
            return False

        if self.pt == self.NINF:
            # -inf, -inf/F; -inf, n/T; -inf, +inf/T
            return other.pt != self.NINF

        if other.pt == self.NINF:
            # n, -inf/F
            return False

        if other.pt == self.PINF:
            # n, +inf/F
            return True

        return self.pt < other.pt

    def __le__(self, other: 'IntervalPoint'):
        if self.pt == self.PINF:
            return other.pt == self.pt # +inf == +inf

        if self.pt == self.NINF:
            return True  # -inf <= -inf, n, +inf

        if other.pt == self.NINF:
            return False 

        if other.pt == self.PINF:
            # _, +inf
            return True

        return self.pt <= other.pt

    def __gt__(self, other: 'IntervalPoint'):
        if self.pt == self.PINF:
            return other.pt != self.PINF

        if self.pt == self.NINF:
            return False

        if other.pt == self.NINF:
            return True

        if other.pt == self.PINF:
            return False

        return self.pt > other.pt

    def __ge__(self, other: 'IntervalPoint'):
        if self.pt == self.PINF:
            # +inf, +inf/T; +inf, n/T; +inf, -inf/T
            return True

        if self.pt == self.NINF:
            # -inf, -inf/T; -inf, n/F; -inf, +inf/F
            return other.pt == self.NINF

        if other.pt == self.NINF:
            # n, -inf;
            return True

        if other.pt == self.PINF:
            return False

        # n, m
        return self.pt >= other.pt

    def __add__(self, o):
        if isinstance(o, IntervalPoint):
            n = o.pt
        elif isinstance(o, int):
            n = o
        else:
            raise NotImplementedError

        sadd = {(self.NINF, self.NINF): self.NINF,
                (self.NINF, self.PINF): None,  # undefined -inf + +inf
                (self.PINF, self.NINF): None,  # undefined: +inf + -inf
                (self.PINF, self.PINF): self.PINF,
                }

        if (self.pt, n) in sadd:
            res = sadd[(self.pt, n)]
            if res is None: raise ValueError(f"Addition not defined on {self.pt} and {n}")
        else:
            if isinstance(self.pt, int) and isinstance(n, int):
                res = self.pt + n
            else:
                # at least one of them is an infinity
                if self.pt != self.NINF and self.pt != self.PINF:
                    res = n    # n + -inf = -inf, n + +inf = +inf
                else:
                    res = self.pt # -inf - n = -inf, +inf - n = +inf

        return IntervalPoint(res)

    def __sub__(self, o):
        if isinstance(o, IntervalPoint):
            n = o.pt
        elif isinstance(o, int):
            n = o
        else:
            raise NotImplementedError

        sadd = {(self.NINF, self.NINF): None,  # undefined -inf - -inf = -inf + +inf
                (self.NINF, self.PINF): self.NINF,  # -inf - +inf
                (self.PINF, self.NINF): self.PINF,  # +inf - -inf
                (self.PINF, self.PINF): None,   # undefined +inf - +inf
        }

        if (self.pt, n) in sadd:
            res = sadd[(self.pt, n)]
            if res is None: raise ValueError(f"Subtraction not defined on {self.pt} and {n}")
        else:
            if isinstance(self.pt, int) and isinstance(n, int):
                res = self.pt - n
            else:
                # at least one of them is an infinity
                if self.pt != self.NINF and self.pt != self.PINF:
                    res = n    # n - -inf = -inf, n - +inf = +inf
                else:
                    res = self.pt # -inf - n = -inf, +inf - n = +inf
        return IntervalPoint(res)

    def __str__(self):
        return f"{self.pt}"

    __repr__ = __str__

# TODO: Define an Interval type

class IntervalsDomain(object):
    PINF = IntervalPoint(IntervalPoint.PINF)
    NINF = IntervalPoint(IntervalPoint.NINF)
    BOT = "BOT"
    TOP = (NINF, PINF)
    finite_height = False

    def phi(self, v: int):
        """Returns an abstract element for a concrete element"""
        return (IntervalPoint(v), IntervalPoint(v)) # this is the math interval [v, v]

    # a best abstraction exists and is equal to phi
    alpha = phi

    def _norm(self, av):
        if isinstance(av, tuple):
            if av[1] == self.NINF: return self.BOT #  ..., -inf)
            if av[0] == self.PINF: return self.BOT #  (+inf, ...

            if av[0] > av[1]: return self.BOT

        return av

    def refine(self, l, r):
        l = self._norm(l)
        r = self._norm(r)

        if l == self.BOT: return r
        if r == self.BOT: return l

        new_start = max(l[0], r[0])
        new_end = min(l[1], r[1])

        return self._norm((new_start, new_end))

    # it helps to think of abstract elements as sets, with lte
    # denoting set inclusion. So we're asking, is x included in y?
    def lte(self, x, y):
        # bot is always less than everything else
        # empty set {} is always included
        x = self._norm(x)
        y = self._norm(y)

        if x is self.BOT: return True
        if y is self.BOT: return False

        # top is only lte
        # top is all possible values, so it is only included in itself
        if x == self.TOP:
            return y == self.TOP

        # check if x is included in y
        if x[0] >= y[0] and x[1] <= y[1]:
            return True

        return False

    def lub(self, x, y):
        '''Least upper bound, the smallest set that includes both x and y'''
        x = self._norm(x)
        y = self._norm(y)

        if self.lte(x, y): return y # y includes x
        if self.lte(y, x): return x # x includes y

        # note neither x nor y can be BOT at this point

        new_left = min(x[0], y[0])
        new_right = max(x[1], y[1])

        return (new_left, new_right)

    def widen(self, x, y):
        logger.debug(f"widen({x}, {y}")

        # assume x is previous and y is current

        # compute union
        u = self.lub(x, y)
        logger.debug(f"widen: u: {u}")

        if u[0] == x[0]:
            # stationary left
            return (u[0], u[1] if u[1] == x[1] else self.PINF)
        elif u[1] == x[1]:
            # stationary right
            return (u[0] if u[0] == x[0] else self.NINF, u[1])
        else:
            return u

        assert False

    def f_binop(self, op, left, right):
        def add(x, y):
            return (x[0] + y[0], x[1] + y[1])

        def sub(x, y):
            a = x[0] - y[1]   # smallest of first interval - largest of second interval
            b = x[1] - y[0]   # largest of first interval - smallest of second interval

            assert a <= b, f"{a}, {b}"
            return (a, b)

        def carry_out_op(op):
            if left == self.BOT or right == self.BOT:
                return self.BOT

            return op(left, right)

        left = self._norm(left)
        right = self._norm(right)

        if op == '+':
            return carry_out_op(lambda x, y: add(x, y))
        elif op == '-':
            return carry_out_op(lambda x, y: sub(x, y))
        else:
            raise NotImplementedError(f'Operator {op}')

    def f_cmpop(self, op, left, c):
        left = self._norm(left)
        c = self._norm(c)

        # assume integers
        if op == '<':
            return (self.NINF, c[0] - 1), (c[0], self.PINF)
        elif op == '<=':
            return (self.NINF, c[0]), (c[0] + 1, self.PINF)
        elif op == '>':
            return (c[0] + 1, self.PINF), (self.NINF, c[0])
        elif op == '>=':
            return (c[0], self.PINF), (self.NINF, c[0] - 1)
        else:
            raise NotImplementedError(f'Operator {op}')

def test_IntervalPoint():
    x = IntervalPoint(5)
    y = IntervalPoint(6)
    pinf = IntervalPoint(IntervalPoint.PINF)
    ninf = IntervalPoint(IntervalPoint.NINF)

    assert not pinf < y
    assert ninf < x
    assert ninf < pinf
    assert ninf <= ninf
    assert y < pinf

    assert pinf > x
    assert y > x

    assert min(ninf, x) == ninf
    assert max(y, pinf) == pinf


if __name__ == "__main__":
    test_IntervalPoint()
