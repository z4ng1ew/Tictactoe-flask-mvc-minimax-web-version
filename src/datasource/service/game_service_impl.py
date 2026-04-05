from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.service.impl import GameServiceImpl, check_winner
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.repository.game_repo import GameRepository
from datasource.mapper.mapper import GameMapper


class GameServiceImplWithRepo(GameServiceInterface):

    def __init__(self, repository: GameRepository):
        self._repo = repository
        self._mapper = GameMapper()

        self._logic = GameServiceImpl()


    def get_next_move(self, game: Game) -> Tuple[int, int]:

        return self._logic.get_next_move(game)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:

        return self._logic.validate_board(game, previous_board)

    def is_game_over(self, game: Game) -> bool:

        return self._logic.is_game_over(game)



    def save_game_state(self, game: Game) -> None:

        game_ds = self._mapper.domain_to_ds(game)
        self._repo.save_game(game_ds)

    def get_previous_board(self, game_id: str) -> GameBoard | None:

        game_ds = self._repo.get_game(game_id)
        if game_ds is None:
            return None
        return self._mapper.ds_to_domain(game_ds).board