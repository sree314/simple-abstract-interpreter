#!/usr/bin/env python3
#
# sem.py
#
# An implementation of the concrete semantics, including an
# interpreter
#
# Author: Sreepathi Pai
#
# Written for CSC2/455 Spring 2020
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to sem.py. This work
# is published from: United States.

from typing import Dict, List
from tinyast import *
import random
import logging

logger = logging.getLogger(__name__)

# map of variables (here str, instead of Var) -> values
#TODO: we could use var if we defined hash to be on the name of Var?
Memory = Dict[str, int]

def f_binop(op: BinaryOps, left: Scalar, right: Scalar) -> Scalar:
    if op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '*':
        return left * right
    elif op == '/':
        return left // right
    else:
        raise NotImplementedError(f"Unknown operator: {op}")

def f_cmpop(op: ComparisonOps, left: Scalar, right: Scalar) -> bool:
    if op == '<':
        return left < right
    elif op == '>':
        return left > right
    elif op == '<=':
        return left <= right
    elif op == '>=':
        return left >= right
    elif op == '!=':
        return left != right
    else:
        raise NotImplementedError(f"Unknown comparison operator: {op}")

def evaluate_Expr(E: Expr, m: Memory) -> Scalar:
    if isinstance(E, Scalar):
        return E
    elif isinstance(E, Var):
        return m[E.name]
    elif isinstance(E, BinOp):
        return f_binop(E.op,
                       evaluate_Expr(E.left, m),
                       evaluate_Expr(E.right, m))


def evaluate_BoolExpr(B: BoolExpr, m: Memory) -> bool:
    return f_cmpop(B.op, m[B.left.name], B.right)

def filter_memory(B: BoolExpr, M: List[Memory], res = True) -> List[Memory]:
    out = [m for m in M if evaluate_BoolExpr(B, m) == res]
    return list(out) #TODO: why materialize this generator?


def union_memories(M0: List[Memory], M1: List[Memory]) -> List[Memory]:
    # this is, of course, ridiculous

    # convert everything to sets
    M0_set = set([frozenset(m.items()) for m in M0])
    M1_set = set([frozenset(m.items()) for m in M1])

    M_set = M0_set.union(M1_set)

    # convert back to lists of dicts
    return list([dict(m) for m in M_set])

# M is a set of memory states, it belongs to Powerset(Memory)
# We're using List, because set would choke on Dict and we don't have a frozendict type...
def evaluate_Cmd(C: Cmd, M: List[Memory]) -> List[Memory]:
    def update_memories(var, value_lambda):
        out = []
        for m in M:
            # not sure using dicts is gaining us anything when we're copying dicts around...
            m_out = dict(m)
            m_out[var] = value_lambda(m)
            out.append(m_out)

        return out

    if isinstance(C, Skip):
        return M
    elif isinstance(C, Program):
        return evaluate_Cmd(C.program, M)
    elif isinstance(C, Assign):
        return update_memories(C.left.name, lambda m: evaluate_Expr(C.right, m))
    elif isinstance(C, Input):
        n = random.randint(0, 100) # could be anything, actually
        return update_memories(C.var.name, lambda _: n)
    elif isinstance(C, Seq):
        return evaluate_Cmd(C.cmd1, evaluate_Cmd(C.cmd0, M))
    elif isinstance(C, IfThenElse):
        then_memory = evaluate_Cmd(C.then_, filter_memory(C.cond, M))
        else_memory = evaluate_Cmd(C.else_, filter_memory(C.cond, M, res = False))

        return union_memories(then_memory, else_memory)
    elif isinstance(C, While):
        # L0 but we apply filter at the end
        out = [m for m in M] # copy all input states

        # the next loop computes L1, L2, L3, ....
        # identify those memories where condition is true

        pre_iter_memories = filter_memory(C.cond, out)
        accum: List[Memory] = []
        while len(pre_iter_memories):
            logger.debug(f"pre_iter_memories: {pre_iter_memories}")
            after_iter_memories = evaluate_Cmd(C.body, pre_iter_memories)
            logger.debug(f"after_iter_memories: {after_iter_memories}")
            accum = union_memories(accum, after_iter_memories)
            logger.debug(f"accum: {accum}")

            # only keep memories where the condition is true for the next iteration
            pre_iter_memories = filter_memory(C.cond, after_iter_memories)

        # This computes L0 U (L1 U L2...) and retains only those memory states where the loop has
        # terminated.
        #
        # we have exited the loop, so only keep those memories where condition is false
        out = filter_memory(C.cond, union_memories(out, accum), res=False)

        return out
    else:
        raise NotImplementedError(f"Don't know how to interpret {type(C).__name__}({C})")

def test_evaluate_Expr():
    x = Var('x')
    y = Var('y')

    m = {'x': 5, 'y': 6}

    x1 = BinOp('+', x, y)
    ex1 = evaluate_Expr(x1, m)
    assert ex1 == 11, ex1

def test_evaluate_BoolExpr():
    x = Var('x')
    y = Var('y')

    m = {'x': 5, 'y': 6}

    b1 = BoolExpr('<', x, 6)
    eb1 = evaluate_BoolExpr(b1, m)
    assert eb1 == True, eb1

def test_evaluate_Cmd():
    #TODO: actually put in asserts for testing. Right now, rely on visual inspection...

    x = Var('x')
    y = Var('y')

    m1 = {'x': 5, 'y': 6}
    m2 = {'x': 8, 'y': 7}

    M_in = [m1, m2]

    s = Program(Skip())
    M_out = evaluate_Cmd(s, M_in)
    print(M_out)

    pasgn = Program(Assign(x, 9))
    M_out = evaluate_Cmd(pasgn, M_in)
    print(M_out)

    pinput = Program(Input(y))
    M_out = evaluate_Cmd(pinput, M_in)
    print(M_out)

    pseq = Program(sequence([Assign(x, 10), Assign(y, 11)]))
    M_out = evaluate_Cmd(pseq, M_in)
    print(M_out)

    pite = Program(IfThenElse(BoolExpr('>', x, 7),
                           Assign(y, BinOp('-', x, 7)),
                           Assign(y, BinOp('-', 7, x))
                           )
                )
    M_out = evaluate_Cmd(pite, M_in)
    print(M_out)

    ploop = Program(While(BoolExpr('<', x, 7),
                          Seq(Assign(y, BinOp('-', y, 1)),
                              Assign(x, BinOp('+', x, 1)))
                    ))
    M_out = evaluate_Cmd(ploop, M_in)
    print(M_in, M_out)

def test_While():
    x = Var('x')
    y = Var('y')

    m1 = {x.name: 4, y.name: 0}
    m2 = {x.name: 8, y.name: 0}
    m3 = {x.name: 5, y.name: 0}
    M_in = [m1, m2, m3]
    print(M_in)

    p = Program(While(BoolExpr('<', x, 7),
                      Seq(Assign(y, BinOp('+', y, 1)),
                          Assign(x, BinOp('+', x, 1)))))
    print(p)
    M_out = evaluate_Cmd(p, M_in)
    print(M_out)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    test_evaluate_Expr()
    test_evaluate_BoolExpr()
    test_evaluate_Cmd()
    test_While()
