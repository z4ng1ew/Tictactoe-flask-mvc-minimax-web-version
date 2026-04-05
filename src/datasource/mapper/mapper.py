import uuid
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.model.game_ds import GameDS
from datasource.model.game_board_ds import GameBoardDS

class GameMapper:
    @staticmethod
    def domain_to_ds(domain_game: Game) -> GameDS:
        # .copy() защищает оригинал от случайных изменений
        board_ds = GameBoardDS(matrix=domain_game.board.matrix.copy(), size=domain_game.board.size)
        return GameDS(id=str(domain_game.id), board=board_ds)

    @staticmethod
    def ds_to_domain(ds_game: GameDS) -> Game:
        board_domain = GameBoard(matrix=ds_game.board.matrix.copy(), size=ds_game.board.size)
        game = Game(board=board_domain)
        # Восстанавливаем UUID из строки
        game.id = uuid.UUID(ds_game.id)
        return game