from dataclasses import dataclass
from datasource.model.game_board_ds import GameBoardDS

@dataclass
class GameDS:
    id: str
    board: GameBoardDS