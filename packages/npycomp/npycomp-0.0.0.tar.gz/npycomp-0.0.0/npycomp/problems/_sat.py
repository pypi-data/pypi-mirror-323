from npycomp.problems._problem import Problem


class SAT(Problem):
    """A SAT problem.

    Parameters
    ----------
    clauses : list
        A list of clauses in conjunctive normal form.

    Attributes
    ----------
    formula : str
        The formula of the problem.
    """

    def __init__(self, clauses: list):
        self._formula = clauses
        Problem.__init__(self, "SAT", clauses=clauses)

    @property
    def formula(self):
        """The formula of the problem."""
        return " ∧ ".join(
            [self._clause_to_string(clause) for clause in self._clauses]
        )

    def _literal_to_string(self, literal: int):
        """Convert a literal to a string.

        Parameters
        ----------
        literal : int
            A literal.
        """
        sign = "¬" if literal & 1 else ""
        return sign + self._variables[literal >> 1]

    def _clause_to_string(self, clause: tuple[int]):
        """Convert a clause to a string.

        Parameters
        ----------
        clause : tuple[int]
            A clause.
        """
        return (
            "(" + " ∨ ".join(self._literal_to_string(l) for l in clause) + ")"
        )

    def _model_to_string(self, model):
        """Convert a model to a string.

        Parameters
        ----------
        model : list
            A list of variable assignments.
        """
        output = []
        for i, assignment in enumerate(model):
            if assignment is None:
                output.append(f"{self._variables[i]} ∈ {{0, 1}}")
            else:
                output.append(f"{self._variables[i]} = {assignment}")

        return ", ".join(output)

    def reconstruct(self, solution):
        """Reconstruct the solution."""
        return solution

    @classmethod
    def from_dimacs(cls, path: str):
        """Load a SAT instance from a DIMACS file.

        Parameters
        ----------
        path: str
            Path to DIMACS-format file describing a SAT instance.

        Returns
        -------
        SAT
            An instance of the SAT class with clauses built from the file.
        """
        clauses = []

        with open(path, "r") as file:
            for line in file:
                line = line.strip()

                if line.startswith("c") or line.startswith("p"):
                    continue

                if line:
                    literals = line.split()
                    clause = []

                    for literal in literals:
                        # End of clause marker
                        if literal == "0":
                            break
                        # Negated literal
                        if literal.startswith("-"):
                            clause.append(f"~{literal[1:]}")
                        # Positive literal
                        else:
                            clause.append(literal)

                    if clause:
                        clauses.append(tuple(clause))
        return cls(clauses)
