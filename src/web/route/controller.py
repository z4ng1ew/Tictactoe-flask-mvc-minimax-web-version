import os
from typing import Tuple
from flask import Flask, request, jsonify, abort, send_from_directory
from domain.service.interface import GameServiceInterface
from web.mapper.mapper import GameWebMapper
from web.model.game_web import GameWeb


def create_game_controller(service: GameServiceInterface) -> Flask:
    """
    Создаёт Flask-приложение с маршрутами для игры.
    :param service: объект, реализующий GameServiceInterface
    :return: настроенный объект Flask
    """
    app = Flask(__name__)

    # =========================================================
    # Вспомогательная функция: сохранить и вернуть ответ
    # =========================================================
    def finish(domain_game):
        """Сохраняет состояние и возвращает JSON-ответ клиенту."""
        service.save_game_state(domain_game)
        return jsonify(GameWebMapper.domain_to_web(domain_game).to_dict()), 200

    # =========================================================
    # Главная страница — отдаём HTML-интерфейс
    # =========================================================
    @app.route('/')
    def serve_frontend():
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        return send_from_directory(static_dir, 'index.html')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        return send_from_directory(static_dir, filename)

    # =========================================================
    # POST /game/<UUID> — основной маршрут игры
    # =========================================================
    @app.route('/game/<string:game_id>', methods=['POST'])
    def handle_game_move(game_id: str):
        """
        Принимает ход игрока, возвращает ответный ход компьютера.

        Порядок:
          1. Проверяем структуру запроса
          2. Проверяем, не изменил ли игрок прошлые ходы
          3. Если игра уже окончена после хода игрока — возвращаем как есть
          4. Компьютер делает ход через Minimax
          5. Если игра окончена после хода компьютера — возвращаем
          6. Игра продолжается — сохраняем и возвращаем
        """

        # --- 1. Валидация (проверка корректности) структуры запроса ---
        data = request.get_json()
        if not data or not isinstance(data, dict):
            abort(400, description="Request body must be a valid JSON object")

        try:
            web_game_input = GameWeb(**data)
            domain_game = GameWebMapper.web_to_domain(web_game_input)
        except (KeyError, ValueError, TypeError) as e:
            abort(400, description=f"Invalid game: {str(e)}")

        # --- 2. Проверяем, не подменил ли игрок прошлые ходы ---
        previous_board = service.get_previous_board(domain_game.id)
        if previous_board is not None:
            if not service.validate_board(domain_game, previous_board):
                abort(400, description="Board validation failed: previous moves were modified")

        # --- 3. Проверяем конец игры после хода игрока ---
        # (победа игрока или ничья — компьютер не ходит)
        if service.is_game_over(domain_game):
            return finish(domain_game)

        # --- 4. Ход компьютера через Minimax ---
        r, c = service.get_next_move(domain_game)
        if r != -1 and domain_game.board.matrix[r][c] == 0:
            domain_game.board.matrix[r][c] = 2  # 2 = компьютер (O)

        # --- 5. Проверяем конец игры после хода компьютера ---
        # (победа компьютера или ничья)
        if service.is_game_over(domain_game):
            return finish(domain_game)

        # --- 6. Игра продолжается ---
        return finish(domain_game)

    return app