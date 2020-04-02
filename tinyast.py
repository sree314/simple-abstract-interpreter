#!/usr/bin/env python3
#
# tinyast.py
#
# An AST for the tiny language presented in Chapter 3 of Rival and Yi.
#
# Author: Sreepathi Pai
#
# Written for CSC2/455 Spring 2020
#
# To the extent possible under law, Sreepathi Pai has waived all
# copyright and related or neighboring rights to tinyast.py. This work
# is published from: United States.

from typing import Union
from typing_extensions import Literal

BinaryOps = Literal['+', '-', '*', '/']
ComparisonOps = Literal['<', '>', '==', '<=', '>=', '!=']

class Node(object):
    pass

class Var(Node):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

Scalar = int # restrict Scalars to ints in this implementation
Expr = Union[Scalar, Var, 'BinOp']

class BinOp(Node):
    def __init__(self, op: BinaryOps, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"({str(self.left)} {self.op} {str(self.right)})"

    __repr__ = __str__

class BoolExpr(Node):
    def __init__(self, op: ComparisonOps, left: Var, right: Scalar):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"{str(self.left)} {self.op} {str(self.right)}"

    __repr__ = __str__

class Cmd(Node):
    pass

class Skip(Cmd):
    def __init__(self):
        pass

    def __str__(self):
        return "skip"

class Seq(Cmd):
    def __init__(self, cmd0: Cmd, cmd1: Cmd):
        self.cmd0 = cmd0
        self.cmd1 = cmd1

    def __str__(self):
        return f"{str(self.cmd0)} ; {str(self.cmd1)}"

class Assign(Cmd):
    def __init__(self, left: Var, right: Expr):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{str(self.left)} := {str(self.right)}"

class Input(Cmd):
    def __init__(self, var: Var):
        self.var = var

    def __str__(self):
        return f"input({self.var})"

class IfThenElse(Cmd):
    def __init__(self, cond: BoolExpr, then_: Cmd, else_: Cmd):
        self.cond = cond
        self.then_ = then_
        self.else_ = else_

    def __str__(self):
        return f"if({str(self.cond)}) {{ {str(self.then_)} }} else {{ { str(self.else_) } }}"

class While(Cmd):
    def __init__(self, cond: BoolExpr, body: Cmd):
        self.cond = cond
        self.body = body

    def __str__(self):
        return f"while({str(self.cond)}) {{ {str(self.body)} }}"

class Program(Node):
    def __init__(self, cmd: Cmd):
        self.program = cmd

    def __str__(self):
        return f"{str(self.program)}"

# convenience function to turn a list into a sequence of cmds
def sequence(l: list) -> Seq:
    if len(l) == 0: raise ValueError("Can't convert an empty list into a Seq")

    if len(l) == 1: return Seq(l[0], Skip())

    return Seq(l[0], sequence(l[1:]))

def test_Program():
    x = Var('x')
    y = Var('y')

    t = Program(IfThenElse(BoolExpr('>', x, 7),
                           Assign(y, BinOp('-', x, 7)),
                           Assign(y, BinOp('-', 7, x))
                           )
                )
    print(t)

if __name__ == "__main__":
    test_Program()

