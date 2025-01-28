from npycomp.problems._problem import Problem


class Clique(Problem):
    """A clique problem.

    Parameters
    ----------
    G : list[list]
        An adjacency matrix.
    k : int
    """

    def __init__(self, A: list[list], k: int):
        self._A = A
        self._k = k
        super().__init__("clique", A=A, k=k)

    def reconstruct(self, solution):
        """Reconstruct the solution."""
        return solution

    @classmethod
    def from_dimacs(cls, path: str, k: int):
        """Load a Clique instance from a DIMACS file.

        Parameters
        ----------
        path : str
            Path to a DIMACS-format file describing a graph.
        k : int
            The size of the clique.

        Returns
        -------
        Clique
            An instance of the Clique class with an adjacency matrix
            built from the file.
        """
        n = 0  # number of vertices
        m = 0  # number of edges
        adjacency = []

        with open(path, "r") as f:
            for line in f:
                # Skip comments
                if line.startswith("c"):
                    continue

                # Problem line: p edge n m
                if line.startswith("p"):
                    parts = line.strip().split()
                    # Typically: p edge n m
                    n = int(parts[2])
                    m = int(parts[3])
                    adjacency = [[0] * n for _ in range(n)]

                # Edge line: e v1 v2
                elif line.startswith("e"):
                    parts = line.strip().split()
                    v1 = int(parts[1]) - 1  # convert to 0-based
                    v2 = int(parts[2]) - 1  # convert to 0-based
                    adjacency[v1][v2] = 1
                    adjacency[v2][v1] = 1

        return cls(adjacency, k)
