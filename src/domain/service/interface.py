from abc import ABC, abstractmethod
from typing import Tuple
from domain.model.game import Game
from domain.model.game_board import GameBoard

class GameServiceInterface(ABC):
    @abstractmethod
    def get_next_move(self, game: Game) -> Tuple[int, int]:
        """Возвращает координаты (row, col) следующего хода. Должен использовать Минимакс."""
        pass

    @abstractmethod
    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        """Проверяет, что предыдущие ходы не были изменены."""
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        """Проверяет условие окончания игры."""
        pass