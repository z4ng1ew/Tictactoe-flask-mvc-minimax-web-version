import threading
from typing import Dict, Optional
from datasource.model.game_ds import GameDS

class GameStorage:
    def __init__(self):
        # Обычный словарь Python. Пока не защищён от одновременных записей.
        self._store: Dict[str, GameDS] = {}
        # Замок (Lock). Гарантирует, что только один поток войдёт в блок кода.
        self._lock = threading.Lock()

    def save(self, game: GameDS) -> None:
        # with self._lock: означает «закрыть замок → выполнить код → открыть замок»
        with self._lock:
            self._store[game.id] = game

    def get(self, game_id: str) -> Optional[GameDS]:
        with self._lock:
            return self._store.get(game_id)