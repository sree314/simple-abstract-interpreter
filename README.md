# Simple Abstract Interpreter

This is a simple abstract interpreter for the language described in
Chapter 3 of Rival and Yi, "[Introduction to Static Analysis: An
Abstract Interpretation
Perspective](https://mitpress.mit.edu/books/introduction-static-analysis)",
MIT Press, 2020. The implementation follows that description fairly
closely. The book presents an OCaml based abstract interpreter in
Chapter 7, but this interpreter is not influenced by that.

It implements a Signs value abstraction and an (Integer) Intervals
value abstraction.

There is a full AST, a full concrete interpreter, and a full abstract
interpreter. Note abstract implementations of operators is not yet
complete for the two value abstractions.


