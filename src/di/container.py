# di/container.py
from typing import Any, Dict, Callable, Type
from datasource.storage import GameStorage
from datasource.repository.game_repo import GameRepository
from datasource.service.game_service_impl import GameServiceImplWithRepo
from web.route.controller import create_game_controller

class Container:
    """
    Контейнер зависимостей (Dependency Injection Container).
    Отвечает за создание и управление жизненным циклом объектов.
    """
    
    def __init__(self):
        # Словарь для хранения созданных экземпляров (кэш)
        self._instances: Dict[str, Any] = {}
        # Словарь для хранения фабрик (функций создания)
        self._factories: Dict[str, Callable[[], Any]] = {}
        
        # === РЕГИСТРАЦИЯ ЗАВИСИМОСТЕЙ ===
        
        # 1. GameStorage — singleton (один на всё приложение)
        def create_storage():
            return GameStorage()
        self.register_singleton("storage", create_storage)
        
        # 2. GameRepository — зависит от storage
        def create_repository():
            storage = self.get("storage")  # Берём готовый singleton
            return GameRepository(storage)
        self.register("repository", create_repository)
        
        # 3. GameService — зависит от repository
        def create_service():
            repo = self.get("repository")
            return GameServiceImplWithRepo(repo)
        self.register("service", create_service)
        
        # 4. Flask Controller — зависит от service
        def create_controller():
            service = self.get("service")
            return create_game_controller(service)
        self.register("controller", create_controller)
    
    def register(self, name: str, factory: Callable[[], Any]) -> None:
        """Регистрирует фабрику для создания объекта (не singleton)."""
        self._factories[name] = factory
        # Если объект уже был создан — удаляем, чтобы пересоздать с новыми зависимостями
        self._instances.pop(name, None)
    
    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """Регистрирует фабрику как singleton (создаётся один раз)."""
        self._factories[name] = factory
        # Сразу создаём и сохраняем экземпляр
        self._instances[name] = factory()
    
    def get(self, name: str) -> Any:
        """
        Получает экземпляр по имени.
        Для singleton — возвращает кэшированный, для остальных — создаёт новый.
        """
        if name in self._instances:
            return self._instances[name]  # Возвращаем готовый (singleton)
        
        if name not in self._factories:
            raise ValueError(f"Dependency '{name}' is not registered")
        
        # Создаём новый экземпляр через фабрику
        instance = self._factories[name]()
        return instance