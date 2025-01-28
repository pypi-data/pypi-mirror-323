"""Implementations of reductions between NP-complete problems.

N ``reductions`` provides implementations of reductions between
NP-complete problems. Each reduction in this module is a function that
transforms an instance of one problem into an instance of another problem.
"""

from npycomp.reductions._clique_to_sat import clique_to_sat
