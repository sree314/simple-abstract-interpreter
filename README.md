[![License: CC0-1.0](https://licensebuttons.net/l/zero/1.0/80x15.png)](http://creativecommons.org/publicdomain/zero/1.0/)

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

The source code also uses type annotations, for use with `mypy`. This
is not complete.

## Course Website

This code accompanies Lectures [17](https://www.cs.rochester.edu/~sree/courses/csc-255-455/spring-2020/static/17-pa-ai.pdf), [18](https://www.cs.rochester.edu/~sree/courses/csc-255-455/spring-2020/static/18-ai.pdf) and [19](https://www.cs.rochester.edu/~sree/courses/csc-255-455/spring-2020/static/19-ai-3.pdf) of the [Spring 2020 edition of CSC255/455 Software Analysis and Improvement](https://www.cs.rochester.edu/~sree/courses/csc-255-455/spring-2020/) taught at the University of Rochester.

## Non-simple Abstract Interpreters

Here is an incomplete list of abstract interpreters built for research or production use:

  1. [Astrée](http://www.astree.ens.fr/)
  2. [Infer](https://fbinfer.com/)
  3. [SPARTA](https://github.com/facebookincubator/SPARTA)
  4. [IKOS](https://github.com/NASA-SW-VnV/ikos)
  5. [Crab](https://github.com/seahorn/crab)
  6. [MIRAI](https://github.com/facebookexperimental/MIRAI) (Rust-only)
