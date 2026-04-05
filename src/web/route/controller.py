import os
from flask import Flask, request, jsonify, abort, send_from_directory
from domain.service.interface import GameServiceInterface
from web.mapper.mapper import GameWebMapper
from web.model.game_web import GameWeb


def create_game_controller(service: GameServiceInterface) -> Flask:
    app = Flask(__name__)
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

    def finish(domain_game):
        service.save_game_state(domain_game)
        return jsonify(GameWebMapper.domain_to_web(domain_game).to_dict()), 200

    @app.route('/')
    def serve_frontend():
        return send_from_directory(static_dir, 'index.html')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(static_dir, filename)

    @app.route('/game/<string:game_id>', methods=['POST'])
    def handle_game_move(game_id: str):
        data = request.get_json()
        if not data or not isinstance(data, dict):
            abort(400, description="Request body must be a valid JSON object")

        try:
            domain_game = GameWebMapper.web_to_domain(GameWeb(**data))
        except (KeyError, ValueError, TypeError) as e:
            abort(400, description=f"Invalid game: {str(e)}")

        previous_board = service.get_previous_board(domain_game.id)
        if previous_board is not None:
            if not service.validate_board(domain_game, previous_board):
                abort(400, description="Board validation failed: previous moves were modified")

        if service.is_game_over(domain_game):
            return finish(domain_game)

        r, c = service.get_next_move(domain_game)
        if r != -1 and domain_game.board.matrix[r][c] == 0:
            domain_game.board.matrix[r][c] = 2

        return finish(domain_game)

    return app