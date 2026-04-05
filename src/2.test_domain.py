#!/usr/bin/env python3
"""
Тест для проверки Задания 2 (domain-слой) по чек-листу.
✅ Запуск: строго из корня проекта!
   cd ~/Рабочий\ стол/PY-3_H
   python src/2.test_domain.py
"""
import uuid
import os
import sys
import inspect

# Определяем папку src/ и добавляем её в PYTHONPATH
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def get_full_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к файлу относительно папки src/."""
    return os.path.abspath(os.path.join(src_dir, relative_path))


def test_domain_checklist():
    print("🔍 Проверка Задания 2 (domain-слой) по чек-листу...")
    print("=" * 80)

    passed = 0
    total = 4

    # =========================================================
    # 1) Модель игрового поля в виде целочисленной матрицы
    # =========================================================
    print("\n1) Описана модель игрового поля в виде целочисленной матрицы:")
    try:
        path = get_full_path('domain/model/game_board.py')
        from domain.model.game_board import GameBoard

        board = GameBoard()
        assert hasattr(board, 'matrix') and isinstance(board.matrix, list)
        assert all(isinstance(row, list) for row in board.matrix)
        assert all(isinstance(cell, int) for row in board.matrix for cell in row)
        assert board.size == 3 and len(board.matrix) == 3

        # Проверка copy() (критично для валидации и алгоритмов)
        board_copy = board.copy()
        assert board_copy.matrix == board.matrix and board_copy.matrix is not board.matrix

        print(f"   ✅ GameBoard: целочисленная матрица, size=3, метод copy() — работает.")
        print(f"   📁 Путь: {path}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 2) Модель текущей игры (UUID + поле)
    # =========================================================
    print("\n2) Описана модель текущей игры, у которой есть UUID и игровое поле:")
    try:
        path = get_full_path('domain/model/game.py')
        from domain.model.game import Game
        from domain.model.game_board import GameBoard

        game = Game()
        assert hasattr(game, 'id') and isinstance(game.id, uuid.UUID)
        assert hasattr(game, 'board') and isinstance(game.board, GameBoard)

        # Проверка возможности передачи своей доски
        custom_board = GameBoard(matrix=[[1, 0, 0], [0, 0, 0], [0, 0, 0]])
        game2 = Game(board=custom_board)
        assert game2.board is custom_board

        print(f"   ✅ Game: уникальный ID (uuid.UUID), поле (GameBoard) — всё на месте.")
        print(f"   📁 Путь: {path}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 3) Интерфейс сервиса с методами (Минимакс, валидация, окончание)
    # =========================================================
    print("\n3) Описан интерфейс сервиса с методами получения хода, валидации и проверки окончания игры:")
    try:
        path_interface = get_full_path('domain/service/interface.py')
        path_impl = get_full_path('domain/service/impl.py')

        from domain.service.interface import GameServiceInterface
        from domain.service.impl import GameServiceImpl
        from domain.model.game import Game
        from domain.model.game_board import GameBoard
        from abc import ABC

        # 1. Проверка, что это абстрактный класс
        assert issubclass(GameServiceInterface, ABC)
        required_methods = {'get_next_move', 'validate_board', 'is_game_over'}
        assert required_methods.issubset(GameServiceInterface.__abstractmethods__)

        # 2. Интерфейс нельзя инстанциировать напрямую
        try:
            GameServiceInterface()
            assert False
        except TypeError:
            pass  # Ожидаемое поведение

        # 3. Проверка реализации
        service = GameServiceImpl()
        empty = GameBoard()
        one_move = GameBoard(matrix=[[1, 0, 0], [0, 0, 0], [0, 0, 0]])
        game = Game(board=one_move)

        # Валидация
        assert service.validate_board(game, one_move) == False, "0 изменений = невалидно"
        assert service.validate_board(game, empty) == True, "1 изменение = валидно"

        # Окончание игры
        assert service.is_game_over(game) == False
        full_game = Game(board=GameBoard(matrix=[[1, 2, 1], [2, 1, 2], [1, 2, 1]]))
        assert service.is_game_over(full_game) == True

        # Следующий ход
        move = service.get_next_move(game)
        assert isinstance(move, tuple) and len(move) == 2
        assert all(isinstance(x, int) for x in move)

        print(f"   ✅ GameServiceInterface: 3 абстрактных метода.")
        print(f"   ✅ GameServiceImpl: логика валидации, хода и окончания игры — работает.")
        print(f"   📁 Интерфейс: {path_interface}")
        print(f"   📁 Реализация: {path_impl}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 4) Модели, интерфейсы, реализации в разных файлах
    # =========================================================
    print("\n4) Модели, интерфейсы, реализации находятся в разных файлах:")
    try:
        files_map = {
            'Модель поля': 'domain/model/game_board.py',
            'Модель игры': 'domain/model/game.py',
            'Интерфейс сервиса': 'domain/service/interface.py',
            'Реализация сервиса': 'domain/service/impl.py'
        }

        full_paths = []
        for name, rel_path in files_map.items():
            full_path = get_full_path(rel_path)
            assert os.path.exists(full_path), f"Файл не найден: {rel_path}"
            with open(full_path, 'r', encoding='utf-8') as f:
                assert 'class ' in f.read(), f"Не найдено определение класса в {full_path}"
            print(f"   ✅ {name}: {full_path}")
            full_paths.append(full_path)

        # Убеждаемся, что все пути уникальны
        assert len(set(full_paths)) == len(full_paths), "Некоторые компоненты находятся в одном файле"
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # ИТОГ
    # =========================================================
    print("\n" + "=" * 80)
    if passed == total:
        print(f"🎉 Все {total} пункта чек-листа пройдены!")
        print("✅ Задание 2 (domain-слой) выполнено полностью.")
        return True
    else:
        print(f"⚠️  Пройдено: {passed} из {total} пунктов")
        print("❌ Проверь ошибки выше")
        return False


if __name__ == "__main__":
    success = test_domain_checklist()
    exit(0 if success else 1)