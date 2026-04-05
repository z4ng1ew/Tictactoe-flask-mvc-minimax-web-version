# Импортируем декоратор dataclass из стандартной библиотеки
from dataclasses import dataclass

# @dataclass — декоратор: автоматически создаёт __init__, __repr__, __eq__
@dataclass
class GameBoardWeb:
    # matrix — переменная класса, тип: список списков целых чисел
    matrix: list[list[int]]
    # size — переменная со значением по умолчанию 3
    size: int = 3