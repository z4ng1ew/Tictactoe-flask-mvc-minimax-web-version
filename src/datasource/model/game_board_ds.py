from dataclasses import dataclass

@dataclass
class GameBoardDS:
    matrix: list[list[int]]
    size: int = 3