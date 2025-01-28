from npycomp._include._graph import _Graph


def clique_to_sat(A: list[list], k: int) -> list:
    """Reduce a clique problem to a SAT problem.

    Consider the problem of determining whether a graph G on n vertices has a
    clique of size k. The reduction to SAT is as follows.

    Let y_{i, r} be a boolean variable indicating whether vertex i is the rth
    vertex in the clique, for i in {1, ..., n} and r in {1, ..., k}. A CNF
    formula that will be satisfiable if and only if there is a clique of size k
    in G is constructed as follows.

    1. For each r, some node must be the rth node of the clique:
    (y_{1, r} ∨ ... ∨ y_{n, r}), for r in {1, ..., k}.

    2. For each i, r < s, if node i is the rth node of the clique, it cannot
    also be the sth node of the clique:
    (¬y_{i, r} ∨ ¬y_{i, s}), for i in {1, ..., n}, s in {1, ..., k}, and r in
    {1, ..., s - 1}.

    3. For each r, s, r ≠ s, if nodes i, j are not connected in G, then they
    cannot both be in the clique:
    (¬y_{i, r} ∨ ¬y_{j, s}), for (i, j) not in E(G), r, s in {1, ..., k}, and
    r ≠ s.

    This reduction produces a SAT instance with O(n^2k^2) clauses.

    Parameters
    ----------
    A : list[list]
        An adjacency matrix.
    k : int
        The size of the clique.

    Returns
    -------
    list
        A list of SAT clauses in conjunctive normal form.
    """
    clauses = []
    G = _Graph(A)
    complement = G.complement
    for r in range(k):
        clause = [f"y_{i}_{r}" for i in range(G.n)]
        clauses.append(clause)

    for i in range(G.n):
        for s in range(k):
            for r in range(s):
                clauses.append([f"~y_{i}_{r}", f"~y_{i}_{s}"])

    for r in range(k):
        for s in range(k):
            if r == s:
                continue
            for i, j in complement.edges:
                clauses.append([f"~y_{i}_{r}", f"~y_{j}_{s}"])

    return clauses
