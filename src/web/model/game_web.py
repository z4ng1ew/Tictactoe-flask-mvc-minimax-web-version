from dataclasses import dataclass
from web.model.game_board_web import GameBoardWeb

@dataclass
class GameWeb:
    id: str
    board: GameBoardWeb

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'board': {
                'matrix': self.board.matrix,
                'size': self.board.size
            }
        }