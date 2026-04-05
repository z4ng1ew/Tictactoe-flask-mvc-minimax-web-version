from typing import List

class GameBoard:
    """Модель игрового поля (целочисленная матрица)"""
    def __init__(self, matrix: List[List[int]] | None = None, size: int = 3):
        if matrix is None:
            self.matrix = [[0] * size for _ in range(size)]
        else:
            # Делаем глубокую копию, чтобы не менять оригинал случайно
            self.matrix = [row[:] for row in matrix]
        self.size = len(self.matrix)

    def copy(self) -> "GameBoard":
        """Возвращает копию поля (понадобится для Минимакса и валидации)"""
        return GameBoard(self.matrix)