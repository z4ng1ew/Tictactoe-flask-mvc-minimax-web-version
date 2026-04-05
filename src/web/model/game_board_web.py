from dataclasses import dataclass

@dataclass
class GameBoardWeb:
    matrix: list[list[int]]
    size: int = 3