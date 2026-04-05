from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.model.game import Game
from domain.model.game_board import GameBoard


class GameServiceImpl(GameServiceInterface):

    def get_next_move(self, game: Game) -> Tuple[int, int]:
        matrix = [row[:] for row in game.board.matrix]

        best_score = float('-inf')  
        best_move = (-1, -1)   

        for r in range(game.board.size):
            for c in range(game.board.size):
                if matrix[r][c] == 0:            
                    matrix[r][c] = 2             
                    score = self._minimax(matrix, depth=0, is_maximizing=False)
                    matrix[r][c] = 0             
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)       

        return best_move

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:

        if game.board.size != previous_board.size:
            return False

        diff_count = 0
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] != previous_board.matrix[r][c]:
                    diff_count += 1

        return diff_count == 1

    def is_game_over(self, game: Game) -> bool:
        if check_winner(game.board.matrix) != 0:
            return True

        if all(cell != 0 for row in game.board.matrix for cell in row):
            return True

        return False


    def _minimax(self, matrix: list, depth: int, is_maximizing: bool) -> int:

        winner = check_winner(matrix)

        if winner == 2:   
            return 10 - depth  
        if winner == 1:   
            return depth - 10  
        if all(cell != 0 for row in matrix for cell in row):
            return 0     

        if is_maximizing:
            best = float('-inf')
            for r in range(3):
                for c in range(3):
                    if matrix[r][c] == 0:
                        matrix[r][c] = 2                              
                        score = self._minimax(matrix, depth + 1, False)  
                        matrix[r][c] = 0                              
                        best = max(best, score)
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if matrix[r][c] == 0:
                        matrix[r][c] = 1                             
                        score = self._minimax(matrix, depth + 1, True)  
                        matrix[r][c] = 0                           
                        best = min(best, score)
            return best



def check_winner(matrix: list) -> int:
    lines = [

        [(0,0), (0,1), (0,2)],
        [(1,0), (1,1), (1,2)],
        [(2,0), (2,1), (2,2)],

        [(0,0), (1,0), (2,0)],
        [(0,1), (1,1), (2,1)],
        [(0,2), (1,2), (2,2)],

        [(0,0), (1,1), (2,2)],
        [(0,2), (1,1), (2,0)],
    ]

    for line in lines:
        cells = [matrix[r][c] for r, c in line]
        if cells[0] != 0 and cells[0] == cells[1] == cells[2]:
            return cells[0]  
            
    return 0  