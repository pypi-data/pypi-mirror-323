class _Graph:
    def __init__(self, A: list[list]):
        self._A = A
        self.n = len(A)

    @property
    def edges(self):
        edges = []
        for i in range(self.n):
            for j in range(self.n):
                if self._A[i][j] == 1 and i < j:
                    edges.append((i, j))
        return edges

    @property
    def complement(self):
        A = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                A[i][j] = 1 - self._A[i][j]

        for i in range(self.n):
            A[i][i] = 0
        return _Graph(A)
