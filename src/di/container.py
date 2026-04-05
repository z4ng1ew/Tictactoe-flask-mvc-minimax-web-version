from typing import Any, Dict, Callable, Type
from datasource.storage import GameStorage
from datasource.repository.game_repo import GameRepository
from datasource.service.game_service_impl import GameServiceImplWithRepo
from web.route.controller import create_game_controller

class Container:

    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        
        def create_storage():
            return GameStorage()
        self.register_singleton("storage", create_storage)
        
        def create_repository():
            storage = self.get("storage") 
            return GameRepository(storage)
        self.register("repository", create_repository)
        
        def create_service():
            repo = self.get("repository")
            return GameServiceImplWithRepo(repo)
        self.register("service", create_service)
        
        def create_controller():
            service = self.get("service")
            return create_game_controller(service)
        self.register("controller", create_controller)
    
    def register(self, name: str, factory: Callable[[], Any]) -> None:
        self._factories[name] = factory
        self._instances.pop(name, None)
    
    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        self._factories[name] = factory
        self._instances[name] = factory()
    
    def get(self, name: str) -> Any:

        if name in self._instances:
            return self._instances[name]  
        
        if name not in self._factories:
            raise ValueError(f"Dependency '{name}' is not registered")
        
        instance = self._factories[name]()
        return instance