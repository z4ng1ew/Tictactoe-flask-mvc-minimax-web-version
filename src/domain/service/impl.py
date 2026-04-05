from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.model.game import Game
from domain.model.game_board import GameBoard


class GameServiceImpl(GameServiceInterface):

    # =========================================================
    # ПУБЛИЧНЫЕ МЕТОДЫ ИНТЕРФЕЙСА
    # =========================================================

    def get_next_move(self, game: Game) -> Tuple[int, int]:
        """
        Возвращает координаты лучшего хода компьютера через алгоритм Minimax.
        Если свободных клеток нет — возвращает (-1, -1).
        """
        # Делаем глубокую копию матрицы, чтобы не менять оригинальное поле
        matrix = [row[:] for row in game.board.matrix]

        best_score = float('-inf')  # Начинаем с наихудшего результата для MAX
        best_move = (-1, -1)       # Сюда запишем лучший ход

        # Перебираем все клетки поля
        for r in range(game.board.size):
            for c in range(game.board.size):
                if matrix[r][c] == 0:            # Клетка свободна?
                    matrix[r][c] = 2             # Пробуем поставить ход компьютера (2 = O)
                    score = self._minimax(matrix, depth=0, is_maximizing=False)
                    matrix[r][c] = 0             # Откатываем ход (возвращаем 0)
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)       # Запоминаем лучший ход

        return best_move

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        """
        Проверяет, что игрок не подменил историю ходов.
        Разница между досками должна быть ровно в 1 клетку.
        """
        if game.board.size != previous_board.size:
            return False

        diff_count = 0
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] != previous_board.matrix[r][c]:
                    diff_count += 1

        # Валидно только если изменилась ровно 1 клетка (ход игрока)
        return diff_count == 1

    def is_game_over(self, game: Game) -> bool:
        """
        Проверяет окончание игры.
        Игра окончена если доска заполнена (ничья) ИЛИ есть победитель.
        """
        # Проверка на победителя
        if check_winner(game.board.matrix) != 0:
            return True

        # Проверка на ничью (все клетки заполнены)
        if all(cell != 0 for row in game.board.matrix for cell in row):
            return True

        return False

    # =========================================================
    # ПРИВАТНЫЙ МЕТОД: рекурсия Minimax
    # =========================================================

    def _minimax(self, matrix: list, depth: int, is_maximizing: bool) -> int:
        """
        Рекурсивно оценивает все возможные исходы игры.

        :param matrix:        текущее состояние поля (список списков)
        :param depth:         глубина рекурсии (количество ходов вперёд)
        :param is_maximizing: True = ход компьютера (MAX), False = ход игрока (MIN)
        :return:              оценка позиции: +N = хорошо для компьютера, -N = плохо
        """
        winner = check_winner(matrix)

        # --- Конечные состояния (терминальные узлы дерева) ---
        if winner == 2:   # Компьютер выиграл
            return 10 - depth  # Чем быстрее победа — тем лучше (выше счёт)
        if winner == 1:   # Игрок выиграл
            return depth - 10  # Чем позже проигрыш — тем «менее плохо»
        if all(cell != 0 for row in matrix for cell in row):
            return 0      # Ничья

        if is_maximizing:
            # ХОД КОМПЬЮТЕРА: ищем максимальный счёт
            best = float('-inf')
            for r in range(3):
                for c in range(3):
                    if matrix[r][c] == 0:
                        matrix[r][c] = 2                              # Пробуем ход
                        score = self._minimax(matrix, depth + 1, False)  # Рекурсия
                        matrix[r][c] = 0                              # Откат
                        best = max(best, score)
            return best
        else:
            # ХОД ИГРОКА: ищем минимальный счёт (игрок играет против нас)
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if matrix[r][c] == 0:
                        matrix[r][c] = 1                             # Пробуем ход игрока
                        score = self._minimax(matrix, depth + 1, True)  # Рекурсия
                        matrix[r][c] = 0                             # Откат
                        best = min(best, score)
            return best


# =========================================================
# Вспомогательная функция проверки победителя (используется
# и в этом файле, и в контроллере)
# =========================================================

def check_winner(matrix: list) -> int:
    """
    Проверяет, есть ли победитель на доске.

    :param matrix: игровое поле 3x3 (список списков)
    :return: 1 если выиграл игрок (X), 2 если компьютер (O), 0 если нет победителя
    """
    lines = [
        # Горизонтали
        [(0,0), (0,1), (0,2)],
        [(1,0), (1,1), (1,2)],
        [(2,0), (2,1), (2,2)],
        # Вертикали
        [(0,0), (1,0), (2,0)],
        [(0,1), (1,1), (2,1)],
        [(0,2), (1,2), (2,2)],
        # Диагонали
        [(0,0), (1,1), (2,2)],
        [(0,2), (1,1), (2,0)],
    ]

    for line in lines:
        cells = [matrix[r][c] for r, c in line]
        if cells[0] != 0 and cells[0] == cells[1] == cells[2]:
            return cells[0]  # 1 = игрок, 2 = компьютер

    return 0  # Победителя нет