from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.service.impl import GameServiceImpl
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.repository.game_repo import GameRepository
from datasource.mapper.mapper import GameMapper


class GameServiceImplWithRepo(GameServiceInterface):

    def __init__(self, repository: GameRepository):
        self._repo = repository
        self._mapper = GameMapper()
        self._domain_logic = GameServiceImpl()

    def get_next_move(self, game: Game) -> Tuple[int, int]:
        return self._domain_logic.get_next_move(game)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        return self._domain_logic.validate_board(game, previous_board)

    def is_game_over(self, game: Game) -> bool:
        return self._domain_logic.is_game_over(game)

    def save_game_state(self, game: Game) -> None:
        self._repo.save_game(self._mapper.domain_to_ds(game))

    def get_previous_board(self, game_id: str) -> GameBoard | None:
        ds_game = self._repo.get_game(game_id)
        if ds_game is None:
            return None
        return self._mapper.ds_to_domain(ds_game).board