from domain.service.impl import GameServiceImpl
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.repository.game_repo import GameRepository
from datasource.mapper.mapper import GameMapper


class GameServiceImplWithRepo(GameServiceImpl):

    def __init__(self, repository: GameRepository):
        super().__init__()
        self._repo = repository
        self._mapper = GameMapper()

    def save_game_state(self, game: Game) -> None:
        self._repo.save_game(self._mapper.domain_to_ds(game))

    def get_previous_board(self, game_id: str) -> GameBoard | None:
        ds_game = self._repo.get_game(game_id)
        if ds_game is None:
            return None
        return self._mapper.ds_to_domain(ds_game).board