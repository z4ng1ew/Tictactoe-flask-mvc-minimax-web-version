from datasource.storage import GameStorage
from datasource.model.game_ds import GameDS

class GameRepository:
    def __init__(self, storage: GameStorage):
        self._storage = storage

    def save_game(self, game: GameDS) -> None:
        self._storage.save(game)

    def get_game(self, game_id: str) -> GameDS | None:
        return self._storage.get(game_id)