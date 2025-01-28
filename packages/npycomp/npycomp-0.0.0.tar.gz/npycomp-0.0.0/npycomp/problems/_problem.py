import copy
from abc import ABC, abstractmethod

import npycomp.reductions._directory as directory
from npycomp.problems._sat_solver import _SATSolver


class Problem(ABC):
    """Abstract base class for a problem."""

    def __init__(self, name: str, **kwargs):
        self._name = name
        self._kwargs = kwargs

    @property
    def name(self):
        """Name of the problem."""
        return self._name

    def solve(self):
        """Solve the problem."""
        kwargs = self.reduce("SAT")
        reduction = _SATSolver(**kwargs)
        solution = reduction.solve()
        return self.reconstruct(solution)

    def reconstruct(self, solution):
        """Reconstruct the solution."""
        return NotImplementedError

    def reduce(self, target):
        """Reduce the problem to a target problem."""
        if self.name == target:
            return self._kwargs

        path = directory.path(self.name, target)
        reduction_kwargs = self._kwargs
        current = self.name
        while path:
            next = path.pop()
            reduction_func = directory.INDEX[(current, next)]
            reduction_kwargs = reduction_func(**reduction_kwargs)
            current = next

        return reduction_kwargs
