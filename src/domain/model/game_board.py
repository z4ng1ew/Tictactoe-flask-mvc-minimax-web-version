from typing import List

class GameBoard:
    def __init__(self, matrix: List[List[int]] | None = None, size: int = 3):
        if matrix is None:
            self.matrix = [[0] * size for _ in range(size)]
        else:
            self.matrix = [row[:] for row in matrix]
        self.size = len(self.matrix)

    def copy(self) -> "GameBoard":
        return GameBoard(self.matrix)