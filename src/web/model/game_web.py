from dataclasses import dataclass
from web.model.game_board_web import GameBoardWeb

@dataclass
class GameWeb:
    # id — строка (UUID приходит как строка из HTTP)
    id: str
    # board — объект типа GameBoardWeb
    board: GameBoardWeb

    def to_dict(self) -> dict:
        """Превращает объект в словарь для JSON-сериализации."""
        return {
            'id': self.id,
            'board': {
                'matrix': self.board.matrix,
                'size': self.board.size
            }
        }