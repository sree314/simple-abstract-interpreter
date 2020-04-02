#!/usr/bin/env python3
#
# sem_abs.py
#
# An implementation of the abstract semantics, including an abstract
# interpreter.
#
# Author: Sreepathi Pai
#
# Written for CSC2/455 Spring 2020
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to sem_abs.py. This work
# is published from: United States.

from typing import List, Dict, Union
from tinyast import *
import random
import abstractions
import logging

from sem import evaluate_Cmd # for testing

Abstraction = Union[abstractions.NonRelationalAbstraction]
AbstractMemory = Dict[str, Abstraction]

logger = logging.getLogger(__name__)

def evaluate_Expr_abs(E: Expr, m: AbstractMemory, vabs):
    if isinstance(E, Scalar):
        return vabs.phi(E)
    elif isinstance(E, Var):
        return m[E.name]
    elif isinstance(E, BinOp):
        return vabs.f_binop(E.op,
                            evaluate_Expr_abs(E.left, m, vabs),
                            evaluate_Expr_abs(E.right, m, vabs))

def evaluate_BoolExpr_abs(B: BoolExpr, m: AbstractMemory, vabs):
    return vabs.f_cmpop(B.op, m[B.left.name], vabs.phi(B.right))

def filter_memory_abs(B: BoolExpr, M_abs, vabs) -> List:
    true_abs, false_abs = evaluate_BoolExpr_abs(B, M_abs, vabs)
    var_abs = M_abs[B.left.name]
    logger.debug(f"true: {true_abs}, false: {false_abs}, value: {var_abs}")

    true_abs = vabs.refine(var_abs, true_abs)
    logger.debug(f"refined true: {true_abs}")
    if true_abs != vabs.BOT:
        # may enter true part
        M_abs_true = dict(M_abs)
        M_abs_true[B.left.name] = true_abs
    else:
        M_abs_true = dict([(m, vabs.BOT) for m in M_abs])

    false_abs =  vabs.refine(var_abs, false_abs)
    logger.debug(f"refined false: {false_abs}")

    if false_abs != vabs.BOT:
        # may enter false part
        M_abs_false = dict(M_abs)
        M_abs_false[B.left.name] = false_abs
    else:
        M_abs_false = dict([(m, vabs.BOT) for m in M_abs])

    return M_abs_true, M_abs_false

def abs_iter(F_abs, M_abs, abstraction):
    R = M_abs
    logger.debug(f'M0: {R}')
    k = 1
    while True:
        T = R
        if abstraction.dom.finite_height:
            R = abstraction.union(R, F_abs(R))
        else:
            R = abstraction.widen(R, F_abs(R))

        logger.debug(f'M{k}: {R}')
        if R == T: break
        k = k + 1
        if k > 5: break

    return T

# M_abs is the abstract set of memory states
def evaluate_Cmd_abs(C: Cmd, M_abs: AbstractMemory, abstraction) -> AbstractMemory:
    def update_abs_memories(var, value_lambda):
        out = dict(M_abs)
        out[var] = value_lambda(M_abs)
        return out

    # C[BOT] -> BOT
    if M_abs == abstraction.BOT:
        return M_abs

    # the value abstraction
    v_abs = abstraction.dom

    if isinstance(C, Skip):
        return M_abs
    elif isinstance(C, Program):
        return evaluate_Cmd_abs(C.program, M_abs, abstraction)
    elif isinstance(C, Assign):
        return update_abs_memories(C.left.name, lambda m: evaluate_Expr_abs(C.right, m, v_abs))
    elif isinstance(C, Input):
        return update_abs_memories(C.var.name, lambda _: v_abs.TOP)
    elif isinstance(C, Seq):
        return evaluate_Cmd_abs(C.cmd1, evaluate_Cmd_abs(C.cmd0, M_abs, abstraction), abstraction)
    elif isinstance(C, IfThenElse):
        then_memory, else_memory = filter_memory_abs(C.cond, M_abs, v_abs)
        logger.debug(f"ite: part-wise precondition: then: {then_memory}, else: {else_memory}")
        then_memory = evaluate_Cmd_abs(C.then_, then_memory, abstraction)
        else_memory = evaluate_Cmd_abs(C.else_, else_memory, abstraction)

        logger.debug(f"ite: part-wise postcondition: then: {then_memory}, else: {else_memory}")
        ite_memory = abstraction.union(then_memory, else_memory)

        logger.debug(f"ite: postcondition: {ite_memory}")
        return ite_memory
    elif isinstance(C, While):
        def F_abs(MM_abs):
            pre_memory, _ = filter_memory_abs(C.cond, MM_abs, v_abs)
            post_memory = evaluate_Cmd_abs(C.body, pre_memory, abstraction)
            return post_memory

        return abs_iter(F_abs, M_abs, abstraction)
    else:
        raise NotImplementedError(f"Don't know how to interpret {type(C).__name__}({C})")

def test_evaluate_Cmd_abs():
    #TODO: actually put in asserts for testing. Right now, rely on visual inspection...

    x = Var('x')
    y = Var('y')

    m1 = {'x': 5, 'y': 6}
    m2 = {'x': 8, 'y': 7}

    nra_abs = abstractions.NonRelationalAbstraction(abstractions.IntervalsDomain())
    M_in = [m1, m2]
    M_in_abs = nra_abs.phi(M_in)

    s = Program(Skip())

    M_out_abs = evaluate_Cmd_abs(s, M_in_abs, nra_abs)
    M_out = evaluate_Cmd(s, M_in)

    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

    pasgn = Program(Assign(x, 9))
    M_out = evaluate_Cmd(pasgn, M_in)
    M_out_abs = evaluate_Cmd_abs(pasgn, M_in_abs, nra_abs)
    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

    pinput = Program(Input(y))
    M_out = evaluate_Cmd(pinput, M_in)
    M_out_abs = evaluate_Cmd_abs(pinput, M_in_abs, nra_abs)
    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

    pseq = Program(sequence([Assign(x, BinOp('+', 10, 11)), Assign(y, 11)]))
    M_out = evaluate_Cmd(pseq, M_in)
    M_out_abs = evaluate_Cmd_abs(pseq, M_in_abs, nra_abs)
    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

    print(M_in)
    #M_in_abs = {'x': nra_abs.dom.TOP, 'y': nra_abs.dom.TOP}
    print(M_in_abs)
    pite = Program(IfThenElse(BoolExpr('>', x, 7),
                           Assign(y, BinOp('-', x, 7)),
                           Assign(y, BinOp('-', 7, x)),
                           )
                )
    M_out = evaluate_Cmd(pite, M_in)
    M_out_abs = evaluate_Cmd_abs(pite, M_in_abs, nra_abs)
    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

    print("loop_start")
    print(M_in_abs)
    ploop = Program(While(BoolExpr('<', x, 7),
                          Seq(Assign(y, BinOp('-', y, 1)),
                              Assign(x, BinOp('+', x, 1)))
                    ))
    print(ploop)
    M_out = evaluate_Cmd(ploop, M_in)
    M_out_abs = evaluate_Cmd_abs(ploop, M_in_abs, nra_abs)
    print(M_in, M_out)
    print(M_out, M_out_abs)
    assert nra_abs.included(M_out, M_out_abs)

def test_ite_bot_abs():
    x = Var('x')
    y = Var('y')

    m1 = {'x': 5, 'y': 6}
    m2 = {'x': 8, 'y': 7}

    nra_abs = abstractions.NonRelationalAbstraction(abstractions.IntervalsDomain())
    M_in = [m1, m2]
    M_in_abs = nra_abs.phi(M_in)

    pite = Program(IfThenElse(BoolExpr('>', x, 9),
                              Assign(x, 10),
                              Assign(y, BinOp('-', 7, x)),
    )
    )

    M_out = evaluate_Cmd(pite, M_in)
    M_out_abs = evaluate_Cmd_abs(pite, M_in_abs, nra_abs)

    print(M_out, M_out_abs)
    print(nra_abs.included(M_out, M_out_abs))

def test_infinite_loop_abs():
    x = Var('x')

    nra_abs = abstractions.NonRelationalAbstraction(abstractions.IntervalsDomain())
    M_in_abs = {'x': nra_abs.dom.TOP}
    nra_abs.BOT = {'x': nra_abs.dom.BOT}

    ploop2 = Program(Seq(Assign(x, 0),
                         While(BoolExpr('>=', x, 0),
                               Assign(x, BinOp('+', x, 1)))
    ))
    print(ploop2)
    M_out_abs = evaluate_Cmd_abs(ploop2, M_in_abs, nra_abs)
    print(M_out_abs)

def test_infinite_loop_abs_2():
    x = Var('x')

    nra_abs = abstractions.NonRelationalAbstraction(abstractions.IntervalsDomain())
    M_in_abs = {'x': nra_abs.dom.TOP}
    nra_abs.BOT = {'x': nra_abs.dom.BOT}

    ploop3 = Program(Seq(Assign(x, 0),
                         While(BoolExpr('<=', x, 100),
                               IfThenElse(BoolExpr('>=', x, 50),
                                  Assign(x, 10),
                                  Assign(x, BinOp('+', x, 1))
                               ))
    ))
    print(ploop3)
    M_out_abs = evaluate_Cmd_abs(ploop3, M_in_abs, nra_abs)
    print(M_out_abs)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    test_ite_bot_abs()
    test_infinite_loop_abs()
    test_infinite_loop_abs_2()
    test_evaluate_Cmd_abs()
