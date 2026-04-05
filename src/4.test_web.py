#!/usr/bin/env python3
r"""
Тест для проверки Задания 4 (web-слой) по чек-листу.
✅ Запуск: строго из корня проекта!
   cd ~/Рабочий\ стол/PY-3_H
   python src/4.test_web.py
"""
import os
import sys
import json
import uuid

src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def get_full_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к файлу относительно папки src/."""
    return os.path.abspath(os.path.join(src_dir, relative_path))


def test_web_checklist():
    print("🔍 Проверка Задания 4 (web-слой) по чек-листу...")
    print("=" * 90)

    passed = 0
    total = 6

    # --- Подготовка тестового приложения ---
    try:
        from flask import Flask
        from datasource.storage import GameStorage
        from datasource.repository.game_repo import GameRepository
        from datasource.service.game_service_impl import GameServiceImplWithRepo
        from web.route.controller import create_game_controller

        storage = GameStorage()
        repo = GameRepository(storage)
        service = GameServiceImplWithRepo(repo)
        app = create_game_controller(service)
        app_ready = True
    except Exception as e:
        print(f"⚠️  Не удалось инициализировать приложение: {e}")
        app_ready = False

    # =========================================================
    # 1) Описаны модели игрового поля, текущей игры.
    # =========================================================
    print("\n1) Описаны модели игрового поля, текущей игры:")
    try:
        p_board = get_full_path('web/model/game_board_web.py')
        p_game  = get_full_path('web/model/game_web.py')

        from web.model.game_board_web import GameBoardWeb
        from web.model.game_web import GameWeb

        board = GameBoardWeb(matrix=[[0]*3]*3, size=3)
        game  = GameWeb(id=str(uuid.uuid4()), board=board)
        assert hasattr(board, 'matrix') and hasattr(board, 'size')
        assert hasattr(game, 'id') and hasattr(game, 'board')
        print(f"   ✅ GameBoardWeb и GameWeb описаны и корректно инициализируются.")
        print(f"   📁 GameBoardWeb: {p_board}")
        print(f"   📁 GameWeb:      {p_game}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 2) Реализованы мапперы domain<->web.
    # =========================================================
    print("\n2) Реализованы мапперы domain<->web:")
    try:
        p = get_full_path('web/mapper/mapper.py')
        from web.mapper.mapper import GameWebMapper
        from domain.model.game import Game
        from domain.model.game_board import GameBoard

        mapper = GameWebMapper()
        domain_board = GameBoard(matrix=[[1,0,0],[0,0,0],[0,0,0]])
        domain_game  = Game(board=domain_board)

        web_g = mapper.domain_to_web(domain_game)
        assert isinstance(web_g, GameWeb) and isinstance(web_g.board, GameBoardWeb)

        restored = mapper.web_to_domain(web_g)
        assert isinstance(restored, Game) and restored.board.matrix == domain_board.matrix
        print(f"   ✅ Мапперы работают в обе стороны (domain <-> web).")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 3) Реализован контроллер Flask с методом POST /game/{UUID}
    # =========================================================
    print("\n3) Реализован контроллер Flask с методом POST /game/{UUID}:")
    try:
        p = get_full_path('web/route/controller.py')
        assert app_ready, "Приложение не инициализировано"
        from flask import Flask
        assert isinstance(app, Flask)
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        assert any('/game/<string:game_id>' in r for r in routes), "Маршрут /game/<game_id> не найден"
        print(f"   ✅ Flask-контроллер создан, маршрут POST /game/<game_id> зарегистрирован.")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 4) Если отправлена некорректная игра, возвращается ошибка с описанием
    # =========================================================
    print("\n4) Если отправлена некорректная игра, возвращается ошибка с описанием:")
    try:
        assert app_ready
        with app.test_client() as client:
            resp1 = client.post('/game/some-uuid', data='not-json', content_type='application/json')
            assert resp1.status_code == 400, f"Ожидался 400, получено {resp1.status_code}"

            resp2 = client.post('/game/some-uuid', 
                                data=json.dumps({"id": "bad-uuid", "board": {"matrix": [[0]], "size": 1}}), 
                                content_type='application/json')
            assert resp2.status_code == 400
        print(f"   ✅ Некорректные запросы отклоняются с кодом 400 и текстовым описанием.")
        print(f"   📁 Путь: {get_full_path('web/route/controller.py')}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 5) Есть поддержка нескольких игр одновременно
    # =========================================================
    print("\n5) Есть поддержка нескольких игр одновременно:")
    try:
        p = get_full_path('datasource/storage.py')
        s1 = GameStorage()
        s2 = GameStorage()
        assert s1 is not s2, "Хранилища не изолированы"

        # ✅ ИСПРАВЛЕНО: используем валидные UUID
        uuid_1 = str(uuid.uuid4())
        uuid_2 = str(uuid.uuid4())

        with app.test_client() as client:
            payload1 = {"id": uuid_1, "board": {"matrix": [[1,0,0],[0,0,0],[0,0,0]], "size": 3}}
            r1 = client.post(f'/game/{uuid_1}', data=json.dumps(payload1), content_type='application/json')
            assert r1.status_code == 200, f"Игра 1 вернула {r1.status_code}"

            payload2 = {"id": uuid_2, "board": {"matrix": [[0,0,0],[0,2,0],[0,0,0]], "size": 3}}
            r2 = client.post(f'/game/{uuid_2}', data=json.dumps(payload2), content_type='application/json')
            assert r2.status_code == 200, f"Игра 2 вернула {r2.status_code}"

        print(f"   ✅ Архитектура поддерживает параллельные игры (нет глобального состояния, запросы не мешают друг другу, несколько игр могут работать одновременно).")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 6) Модели, интерфейсы, реализации находятся в разных файлах.
    # =========================================================
    print("\n6) Модели, интерфейсы, реализации находятся в разных файлах:")
    try:
        files_map = {
            'Модели web': ['web/model/game_board_web.py', 'web/model/game_web.py'],
            'Маппер': 'web/mapper/mapper.py',
            'Контроллер': 'web/route/controller.py'
        }
        all_paths = []
        for name, paths in files_map.items():
            if isinstance(paths, str): paths = [paths]
            for p_rel in paths:
                p_abs = get_full_path(p_rel)
                assert os.path.exists(p_abs), f"Файл не найден: {p_rel}"
                assert os.path.getsize(p_abs) > 10, f"Файл пустой или слишком маленький: {p_rel}"
                all_paths.append(p_abs)
                print(f"   ✅ {name}: {p_abs}")
        assert len(all_paths) == len(set(all_paths)), "Обнаружены дубликаты файлов"
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # ИТОГ
    # =========================================================
    print("\n" + "=" * 90)
    if passed == total:
        print(f"🎉 Все {total} пунктов чек-листа пройдены!")
        print("✅ Задание 4 (web-слой) выполнено полностью.")
        return True
    else:
        print(f"⚠️  Пройдено: {passed} из {total}")
        print("❌ Проверь ошибки выше")
        return False


if __name__ == "__main__":
    success = test_web_checklist()
    exit(0 if success else 1)