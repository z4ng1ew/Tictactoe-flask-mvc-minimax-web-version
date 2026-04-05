import uuid
from domain.model.game import Game
from domain.model.game_board import GameBoard
from web.model.game_web import GameWeb
from web.model.game_board_web import GameBoardWeb

class GameWebMapper:
    @staticmethod
    def domain_to_web(domain_game: Game) -> GameWeb:
        board_web = GameBoardWeb(
            matrix=domain_game.board.matrix.copy(),
            size=domain_game.board.size
        )
        return GameWeb(id=str(domain_game.id), board=board_web)

    @staticmethod
    def web_to_domain(web_game: GameWeb) -> Game:
        if isinstance(web_game.board, dict):
            matrix = web_game.board['matrix']
            size = web_game.board.get('size', 3)  
        else:
            matrix = web_game.board.matrix
            size = web_game.board.size

        board_domain = GameBoard(matrix=matrix.copy(), size=size)

        game = Game(board=board_domain)
        
        if isinstance(web_game.id, str):
            game.id = uuid.UUID(web_game.id)
        else:
            game.id = web_game.id
            
        return game