class _SATSolver:
    """SAT solver.

    This class is not part of the public API. It exists to avoid self-reference
    in `SAT.reduce()`.
    """

    def __init__(self, clauses: list):
        self._variable_table = {}
        self._variables = []
        self._clauses = [self._parse_clause(clause) for clause in clauses]
        self._unit_clauses = []
        self._pure_literals = []

    def _parse_clause(self, clause: tuple[str]) -> tuple[int]:
        """Parse a clause.

        Variables are encoded as numbers 0 to n-1, where n is the number of
        variables. Positive literals with variables encoded with integer
        x are encoded as 2x, and negated literals are encoded as 2*x + 1. A
        parsed clause is a tuple of encoded literals.

        Parameters
        ----------
        clause : tuple[str]
            A clause.

        Returns
        -------
        tuple[int]
            A parsed clause.
        """
        parsed_clause = []
        for literal in clause:
            negated = 1 if literal.startswith("~") else 0
            variable = literal[negated:]
            if variable not in self._variable_table:
                self._variable_table[variable] = len(self._variables)
                self._variables.append(variable)
            encoded_literal = self._variable_table[variable] << 1 | negated
            parsed_clause.append(encoded_literal)
        return tuple(set(parsed_clause))

    def _unit_clauses_exist(self, clauses):
        """Check if unit clauses exist.

        A unit clause is a clause with only one unassigned literal.

        Parameters
        ----------
        clauses : list
            A list of clauses.
        """
        self._unit_clauses = [c for c in clauses if len(c) == 1]
        return bool(self._unit_clauses)

    def _unit_propagation(self, clauses, model):
        """Perform unit propagation.

        Remove every clause containing a unit clause's literaly, and remove
        the negation of the unit clause's literal from every clause.

        Parameters
        ----------
        clauses : list
            A list of clauses.
        model : list
            A list of variable assignments.
        """
        unit_literals = set([literal for (literal,) in self._unit_clauses])
        while unit_literals:
            literal = unit_literals.pop()
            clauses = [c for c in clauses if literal not in c]
            clauses = [
                tuple([l for l in c if l != literal ^ 1]) for c in clauses
            ]
            if model[literal >> 1] is None:
                model[literal >> 1] = int(literal & 1 == 0)

        return clauses, model

    def _pure_literals_exist(self, clauses):
        """Check if pure literals exist.

        A pure literal is a literal that appears with the same sign in all
        clauses.

        Parameters
        ----------
        clauses : list
            A list of clauses.
        """
        literals = set()
        for clause in clauses:
            literals.update(clause)
        pure_literals = set()
        for literal in literals:
            if literal ^ 1 not in literals:
                pure_literals.add(literal)

        self._pure_literals = pure_literals
        return bool(pure_literals)

    def _pure_literal_elimination(self, clauses, model):
        """Perform pure literal elimination.

        Remove every clause containing a pure literal, and assign the pure
        literal to the value that makes the clause true.

        Parameters
        ----------
        clauses : list
            A list of clauses.
        model : list
            A list of variable assignments.
        """
        for literal in self._pure_literals:
            clauses = [clause for clause in clauses if literal not in clause]
            model[literal >> 1] = int(literal & 1 == 0)
        return clauses, model

    def _dpll(self, clauses, model):
        """Perform the DPLL procedure.

        Implementation of The Davis–Putnam–Logemann–Loveland (DPLL) recursive
        backtracking procedure for solving the SAT problem. The algorithm
        performs unit propagation and pure literal elimination to simplify the
        formula, and then recursively assigns values to variables until a
        solution is found or the formula is unsatisfiable.

        Unit propagation: If a clause contains only one unassigned literal,
        assign the literal to the value that makes the clause true. Remove
        every clause containing the literal, and remove the negation of the
        literal from every clause.

        Pure literal elimination: If a literal appears with the same sign in
        all clauses, assign the literal to the value that makes the clauses
        true. Remove every clause containing the literal.

        Parameters
        ----------
        clauses : list
            A list of clauses.
        model : list
            A list of variable assignments
        """
        # Unit propagation
        while self._unit_clauses_exist(clauses):
            clauses, model = self._unit_propagation(clauses, model)
        # Pure literal elimination
        while self._pure_literals_exist(clauses):
            clauses, model = self._pure_literal_elimination(clauses, model)
        # Stopping conditions
        if not clauses:
            return model
        if any(not clause for clause in clauses):
            return False

        # DPLL procedure
        try:
            variable = model.index(None)
        except:
            return False
        for literal in (variable << 1, variable << 1 | 1):
            solution = self._dpll(
                [*clauses, (literal,)],
                [
                    *model[:literal],
                    int(literal & 1 == 0),
                    *model[literal + 1 :],
                ],
            )
            if solution:
                return solution

        return False

    def solve(self):
        """Solve the problem."""
        model = self._dpll(self._clauses, [None] * len(self._variables))
        return model
