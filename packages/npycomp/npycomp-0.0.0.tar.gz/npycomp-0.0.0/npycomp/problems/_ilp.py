from npycomp.problems._problem import Problem


class ILP(Problem):
    """A 0-1 integer linear programming problem.

    Parameters
    ----------
    c : list[list]
        A matrix of coefficients.
    d : list
        A vector of targets.
    """

    def __init__(self, c: list[list], d: list):
        self._c = c
        self._d = d
        super().__init__(self, "0-1 ILP")

    def reduce(self, target: Problem):
        """Reduce the problem to a target problem."""
        pass

    def reconstruct(self, solution):
        """Reconstruct the solution."""
        return solution
