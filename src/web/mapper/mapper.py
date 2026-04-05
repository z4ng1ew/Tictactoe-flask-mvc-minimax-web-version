import uuid
from domain.model.game import Game
from domain.model.game_board import GameBoard
from web.model.game_web import GameWeb
from web.model.game_board_web import GameBoardWeb

class GameWebMapper:
    @staticmethod
    def domain_to_web(domain_game: Game) -> GameWeb:
        """Переводит domain-модель в web-модель (для отправки клиенту)."""
        # Здесь всё просто: domain-объекты гарантированно имеют нужные атрибуты
        board_web = GameBoardWeb(
            matrix=domain_game.board.matrix.copy(),
            size=domain_game.board.size
        )
        return GameWeb(id=str(domain_game.id), board=board_web)

    @staticmethod
    def web_to_domain(web_game: GameWeb) -> Game:
        """
        Переводит web-модель в domain-модель (для обработки логики).
        УМЕЕТ работать как с объектами, так и со словарями (dict).
        """
        # --- 1. Извлекаем данные доски (матрицу и размер) ---
        # Проверяем тип: если пришёл словарь (из JSON) или объект (из теста)
        if isinstance(web_game.board, dict):
            # Если словарь — достаём значения по ключам
            matrix = web_game.board['matrix']
            size = web_game.board.get('size', 3)  # get с дефолтом, чтобы не упасть
        else:
            # Если уже объект — достаём через точку
            matrix = web_game.board.matrix
            size = web_game.board.size

        # --- 2. Создаём domain-модель доски ---
        # .copy() обязателен, чтобы не мутировать входящие данные
        board_domain = GameBoard(matrix=matrix.copy(), size=size)

        # --- 3. Создаём domain-модель игры ---
        game = Game(board=board_domain)
        
        # --- 4. Восстанавливаем UUID ---
        # uuid.UUID() умеет принимать и строку, и уже готовый UUID
        if isinstance(web_game.id, str):
            game.id = uuid.UUID(web_game.id)
        else:
            game.id = web_game.id
            
        return game