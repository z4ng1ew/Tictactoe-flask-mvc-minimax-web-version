import threading
from typing import Dict, Optional
from datasource.model.game_ds import GameDS

class GameStorage:
    def __init__(self):

        self._store: Dict[str, GameDS] = {}
        self._lock = threading.Lock()

    def save(self, game: GameDS) -> None:
        with self._lock:
            self._store[game.id] = game

    def get(self, game_id: str) -> Optional[GameDS]:
        with self._lock:
            return self._store.get(game_id)