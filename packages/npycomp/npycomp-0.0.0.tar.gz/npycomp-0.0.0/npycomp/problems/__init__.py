"""Implementations of various NP-complete problems.

.. currentmodule:: npycomp.problems

NPyComp ``solvers`` provides implementations of various NP-complete problems.
Each problem in this module is reducible to any other problem in this module.
"""

from npycomp.problems._clique import Clique
from npycomp.problems._sat import SAT
