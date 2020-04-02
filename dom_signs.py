#!/usr/bin/env python3
#
# dom_signs.py
#
# Implementation of a signs value abstraction.
#
# Author: Sreepathi Pai
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to dom_signs.py. This
# work is published from: United States.
#
# Note: This is still incomplete, but should throw NotImplementedErrors
#
import logging

logger = logging.getLogger(__name__)

#TODO: this is really a static class/enum?
class SignsDomain(object):
    LTZ = "[<= 0]"
    GTZ = "[>= 0]"
    EQZ = "[= 0]"
    TOP = "TOP"
    BOT = "BOT"
    finite_height = True

    def phi(self, v: int):
        """Returns an abstract element for a concrete element"""
        if v == 0:
            return self.EQZ
        elif v > 0:
            return self.GTZ
        elif v < 0:
            return self.LTZ
        else:
            raise ValueError(f"Unknown value for signs abstraction {v}")

    # a best abstraction exists and is equal to phi
    alpha = phi

    # it helps to think of abstract elements as sets, with lte
    # denoting set inclusion. So we're asking, is x included in y?
    def lte(self, x, y):
        # bot is always less than everything else
        # empty set {} is always included
        if x == self.BOT: return True

        # top is only lte
        # top is all possible values, so it is only included in itself
        if x == self.TOP:
            if y != self.TOP: return False
            return True

        # eqz is the set {0}, which is included in all sets (>=0, <=0) except {}
        if x == self.EQZ:
            if y == self.BOT: return False
            return True

        if x == self.LTZ or x == self.GTZ:
            if y == x: return True
            if y == self.TOP: return True

            # these sets are not included in {0} or {} or {>=0} [resp. {<=0}]
            return False

    def lub(self, x, y):
        '''Least upper bound, the smallest set that includes both x and y'''

        if self.lte(x, y): return y # y includes x
        if self.lte(y, x): return x # x includes y

        # if incomparable, then we return T
        return self.TOP

    def f_binop(self, op, left, right):
        if op == '+':
            return self.lub(left, right)
        elif op == '*':
            if left != right:
                return self.lub(left, right)
            elif left == self.LTZ:
                return self.GTZ  # - * - = +
            elif left == self.GTZ:
                return self.GTZ  # + * + = +
        elif op == '-':
            if left == right:
                if left != self.EQZ and left != self.BOT:
                    return self.TOP

                return left # {0} - {0} => {0}, {} - {} => {}
            else:
                return left   # {+ve} - {-ve} => positive, {-ve} - {+ve} => {-ve}

        else:
            raise NotImplementedError(f'Operator {op}')

    def refine(self, l, r):
        if self.lte(l, r): return l
        if self.lte(r, l): return r

        return self.TOP

    def f_cmpop(self, op, left, c):
        # (abst of c, op) : (variable's true domain, variables false domain)
        abs_results = {(self.EQZ, '<'): (self.LTZ, self.GTZ),
                       (self.EQZ, '<='): (self.LTZ, self.GTZ),
                       (self.EQZ, '>'): (self.GTZ, self.LTZ),
                       (self.EQZ, '>='): (self.GTZ, self.LTZ),
                       (self.EQZ, '!='): (self.TOP, self.EQZ),

                       (self.GTZ, '>'): (self.GTZ, self.TOP),
                       (self.GTZ, '<'): (self.TOP, self.GTZ),
                       (self.GTZ, '<='): (self.TOP, self.GTZ),
                       (self.GTZ, '>='): (self.GTZ, self.TOP),
                       }

        key = (c, op)
        if key not in abs_results:
            raise NotImplementedError(f"{key} not implemented")

        return abs_results[key]
