"""SATLIB benchmarks for the SAT problem.

Benchmarks are sourced from the SATLIB benchmark suite. The SATLIB benchmark
suite is a collection of SAT instances from various sources, including
randomly generated instances and instances from real-world applications.
All instances are in conjunctive normal form (CNF) and are encoded in the
DIMACS format. See https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/AIM/descr.html.
"""

import glob

import pytest
from npycomp.problems import SAT


@pytest.mark.parametrize(
    "path", glob.glob("tests/test_cases/satlib/aim/50/*.cnf")
)
def test_AIM_50(path):
    """Test SATLIB AIM cases.

    Unsatisfiable instances at low clause/variable ratios. Satisfiable
    instances at low and high clause/variable ratios, with only one solution.
    See https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/DIMACS/AIM/descr.html
    for a complete description of the sampling procedure.
    """
    p = SAT.from_dimacs(path=path)
    model = p.solve()

    if "unsat" in path:
        assert model == False
    else:
        assert model is not None


@pytest.mark.parametrize(
    "path",
    glob.glob("tests/test_cases/satlib/uniform-random-3sat/*.cnf"),
)
def test_uniform_random_3SAT(path):
    """Test SATLIB uniform-random 3-SAT cases.

    Uniform Random-3-SAT, phase transition region, unforced filtered.
    See https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/descr.html
    for a complete description of the sampling procedure.
    """
    p = SAT.from_dimacs(path=path)
    model = p.solve()

    if "unsat" in path:
        assert model == False
    else:
        assert model is not None
