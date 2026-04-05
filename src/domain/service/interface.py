from abc import ABC, abstractmethod
from typing import Tuple
from domain.model.game import Game
from domain.model.game_board import GameBoard

class GameServiceInterface(ABC):
    @abstractmethod
    def get_next_move(self, game: Game) -> Tuple[int, int]:
        pass

    @abstractmethod
    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        pass