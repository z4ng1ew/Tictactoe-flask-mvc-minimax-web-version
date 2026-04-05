import uuid
from domain.model.game_board import GameBoard

class Game:
    """Модель текущей игры: уникальный ID + поле"""
    def __init__(self, board: GameBoard | None = None):
        self.id = uuid.uuid4()
        self.board = board or GameBoard()