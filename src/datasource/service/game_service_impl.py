from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.service.impl import GameServiceImpl, check_winner
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.repository.game_repo import GameRepository
from datasource.mapper.mapper import GameMapper


class GameServiceImplWithRepo(GameServiceInterface):
    """
    Сервис с поддержкой репозитория (хранилища).
    Логику хода (Minimax) делегирует GameServiceImpl из domain-слоя,
    чтобы не дублировать алгоритм.
    """

    def __init__(self, repository: GameRepository):
        self._repo = repository
        self._mapper = GameMapper()
        # Делегат (посредник) для логики игры — берём из domain-слоя
        self._logic = GameServiceImpl()

    # =========================================================
    # МЕТОДЫ ИНТЕРФЕЙСА — делегируем логику в domain-сервис
    # =========================================================

    def get_next_move(self, game: Game) -> Tuple[int, int]:
        """
        Возвращает лучший ход компьютера через Minimax.
        Делегирует вычисление в GameServiceImpl (domain-слой).
        """
        return self._logic.get_next_move(game)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        """
        Проверяет корректность хода игрока (ровно 1 изменение).
        Делегирует в GameServiceImpl.
        """
        return self._logic.validate_board(game, previous_board)

    def is_game_over(self, game: Game) -> bool:
        """
        Проверяет окончание игры: победа или ничья.
        Делегирует в GameServiceImpl (там проверяется и победитель, и ничья).
        """
        return self._logic.is_game_over(game)

    # =========================================================
    # МЕТОДЫ РАБОТЫ С ХРАНИЛИЩЕМ (специфичны для этого слоя)
    # =========================================================

    def save_game_state(self, game: Game) -> None:
        """Сохраняет текущее состояние игры в репозиторий."""
        game_ds = self._mapper.domain_to_ds(game)
        self._repo.save_game(game_ds)

    def get_previous_board(self, game_id: str) -> GameBoard | None:
        """
        Загружает предыдущее состояние доски из репозитория.
        Возвращает None, если игра ещё не начиналась (первый ход).
        """
        game_ds = self._repo.get_game(game_id)
        if game_ds is None:
            return None
        return self._mapper.ds_to_domain(game_ds).board