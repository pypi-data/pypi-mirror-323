"""DIMACS benchmark set for the clique problem.

Benchmarks are sourced from the second DIMACS implementation challenge
(1993), http://dimacs.rutgers.edu/Challenges.

See https://iridia.ulb.ac.be/~fmascia/maximum_clique/DIMACS-benchmark#detC125.9
for the full list of benchmarks.
"""

import pytest
from npycomp.problems import Clique


@pytest.mark.parametrize("k", [1, 2, 3, 4, 5, 6])
def test_c125(k):
    """Test c125.9 instance.

    Graph with 125 nodes, 6,963 edges, and a best known clique of size 34.
    """
    path = "tests/test_cases/clique/c125.9.clq"
    p = Clique.from_dimacs(path=path, k=k)
    model = p.solve()

    assert model is not None


@pytest.mark.parametrize("k", [1, 2, 3])
def test_c250(k):
    """Test c250.9 instance.

    Graph with 250 nodes, 27,984 edges, and a best known clique of size 44.
    """
    path = "tests/test_cases/clique/c250.9.clq"
    p = Clique.from_dimacs(path=path, k=k)
    model = p.solve()

    assert model is not None
