#!/usr/bin/env python3
r"""
Тест для проверки Задания 3 (datasource-слой) по чек-листу.
✅ Запуск: строго из корня проекта!
   cd ~/Рабочий\ стол/PY-3_H
   python src/3.test_datasource.py
"""
import os
import sys
import threading
import inspect

# Добавляем папку src/ в PYTHONPATH, чтобы импорты работали из корня проекта
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def get_full_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к файлу относительно папки src/."""
    return os.path.abspath(os.path.join(src_dir, relative_path))


def test_datasource_checklist():
    print("🔍 Проверка Задания 3 (datasource-слой) по чек-листу...")
    print("=" * 75)

    passed = 0
    total = 7

    # ---------------------------------------------------------
    # 1. Класс-хранилище для хранения текущих игр
    # ---------------------------------------------------------
    print("\n1. Класс-хранилище для хранения текущих игр:")
    try:
        path = get_full_path('datasource/storage.py')
        from datasource.storage import GameStorage
        storage = GameStorage()
        assert hasattr(storage, '_store') and isinstance(storage._store, dict)
        print(f"   ✅ GameStorage реализован (словарь в памяти).")
        print(f"   📁 Путь: {path}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 2. Потокобезопасные коллекции
    # ---------------------------------------------------------
    print("\n2. Потокобезопасные коллекции (threading.Lock):")
    try:
        assert hasattr(storage, '_lock') and callable(getattr(storage._lock, 'acquire', None))
        src_save = inspect.getsource(storage.save)
        assert 'with self._lock:' in src_save
        print(f"   ✅ Хранилище использует Lock для защиты от гонок потоков.")
        print(f"   📁 Путь: {get_full_path('datasource/storage.py')}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 3. Модели игрового поля, текущей игры
    # ---------------------------------------------------------
    print("\n3. Модели игрового поля, текущей игры:")
    try:
        path_board = get_full_path('datasource/model/game_board_ds.py')
        path_game  = get_full_path('datasource/model/game_ds.py')
        from datasource.model.game_board_ds import GameBoardDS
        from datasource.model.game_ds import GameDS
        board = GameBoardDS(matrix=[[0]*3]*3, size=3)
        game  = GameDS(id="test-uuid", board=board)
        assert board.size == 3 and game.id == "test-uuid"
        print(f"   ✅ GameBoardDS и GameDS описаны и корректно инициализируются.")
        print(f"   📁 GameBoardDS: {path_board}")
        print(f"   📁 GameDS:      {path_game}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 4. Мапперы domain <-> datasource
    # ---------------------------------------------------------
    print("\n4. Мапперы domain <-> datasource:")
    try:
        path_mapper = get_full_path('datasource/mapper/mapper.py')
        from datasource.mapper.mapper import GameMapper
        from domain.model.game import Game
        from domain.model.game_board import GameBoard
        
        mapper = GameMapper()
        domain_game = Game(board=GameBoard(matrix=[[1,0,0],[0,0,0],[0,0,0]]))
        ds_game = mapper.domain_to_ds(domain_game)
        restored = mapper.ds_to_domain(ds_game)
        assert isinstance(ds_game, GameDS) and isinstance(restored, Game)
        
        print(f"   ✅ Мапперы реализованы и работают в обе стороны.")
        print(f"   📁 Путь: {path_mapper}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 5. Репозиторий (save / get)
    # ---------------------------------------------------------
    print("\n5. Репозиторий для работы с классом-хранилищем (save_game / get_game):")
    try:
        path_repo = get_full_path('datasource/repository/game_repo.py')
        from datasource.repository.game_repo import GameRepository
        repo = GameRepository(storage)
        repo.save_game(GameDS(id="repo-test", board=GameBoardDS(matrix=[[0]*3]*3)))
        assert repo.get_game("repo-test").id == "repo-test"
        print(f"   ✅ Репозиторий сохраняет и получает игры.")
        print(f"   📁 Путь: {path_repo}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 6. Сервис, реализующий интерфейс и принимающий репозиторий
    # ---------------------------------------------------------
    print("\n6. Сервис, реализующий интерфейс и принимающий репозиторий:")
    try:
        path_service = get_full_path('datasource/service/game_service_impl.py')
        from datasource.service.game_service_impl import GameServiceImplWithRepo
        from domain.service.interface import GameServiceInterface
        
        service = GameServiceImplWithRepo(repo)
        assert isinstance(service, GameServiceInterface)
        print(f"   ✅ Сервис реализует интерфейс и принимает репозиторий через __init__.")
        print(f"   📁 Путь: {path_service}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # 7. Модели, интерфейсы, реализации в разных файлах
    # ---------------------------------------------------------
    print("\n7. Модели, интерфейсы, реализации находятся в разных файлах:")
    try:
        files_map = {
            'Хранилище': 'datasource/storage.py',
            'Модель поля': 'datasource/model/game_board_ds.py',
            'Модель игры': 'datasource/model/game_ds.py',
            'Маппер': 'datasource/mapper/mapper.py',
            'Репозиторий': 'datasource/repository/game_repo.py',
            'Сервис (реализация)': 'datasource/service/game_service_impl.py',
        }
        for name, rel_path in files_map.items():
            full_path = get_full_path(rel_path)
            assert os.path.exists(full_path), f"Файл не найден: {rel_path}"
            print(f"   ✅ {name}: {full_path}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # ---------------------------------------------------------
    # ИТОГ
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    if passed == total:
        print(f"🎉 Все {total} пунктов чек-листа пройдены!")
        print("✅ Задание 3 (datasource-слой) выполнено полностью.")
        return True
    else:
        print(f"⚠️  Пройдено: {passed} из {total}")
        print("❌ Проверь ошибки выше")
        return False


if __name__ == "__main__":
    success = test_datasource_checklist()
    exit(0 if success else 1)