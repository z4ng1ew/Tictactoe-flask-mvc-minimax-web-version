#!/usr/bin/env python3
r"""
Тест для проверки Задания 5 (di-слой) по чек-листу.
✅ Запуск: строго из корня проекта!
   cd ~/Рабочий\ стол/PY-3_H
   python src/5.test_di.py
"""
import os
import sys

src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def get_full_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к файлу относительно папки src/."""
    return os.path.abspath(os.path.join(src_dir, relative_path))


def test_di_checklist():
    print("🔍 Проверка Задания 5 (di-слой) по чек-листу...")
    print("=" * 85)

    passed = 0
    total = 4

    # --- Инициализация контейнера для всех проверок ---
    try:
        from di.container import Container
        container = Container()
        container_ready = True
    except Exception as e:
        print(f"⚠️  Не удалось создать Container: {e}")
        container_ready = False

    # =========================================================
    # 1) Реализован класс Container, в котором описывается граф зависимостей.
    # =========================================================
    print("\n1) Реализован класс Container, в котором описывается граф зависимостей:")
    try:
        p = get_full_path('di/container.py')
        assert container_ready, "Container не инициализирован"

        # Проверяем наличие механизмов регистрации/получения
        assert hasattr(container, 'get') or hasattr(container, 'resolve')

        # Проверяем, что граф разрешается полностью (запрос контроллера тянет всю цепочку)
        from flask import Flask
        app = container.get("controller")
        assert isinstance(app, Flask), "Граф не разрешился до Flask-приложения"

        print(f"   ✅ Класс Container реализован и корректно разрешает граф зависимостей.")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 2) Класс-хранилище определён в качестве singleton.
    # =========================================================
    print("\n2) Класс-хранилище определён в качестве singleton:")
    try:
        p = get_full_path('di/container.py')
        assert container_ready

        storage1 = container.get("storage")
        storage2 = container.get("storage")
        assert storage1 is storage2, "Хранилище не является singleton (возвращаются разные объекты)"

        from datasource.storage import GameStorage
        assert isinstance(storage1, GameStorage)

        print(f"   ✅ GameStorage зарегистрирован как singleton (один экземпляр на всё приложение).")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 3) Определён репозиторий для работы с классом-хранилищем.
    # =========================================================
    print("\n3) Определён репозиторий для работы с классом-хранилищем:")
    try:
        p = get_full_path('datasource/repository/game_repo.py')
        assert container_ready

        repo = container.get("repository")
        from datasource.repository.game_repo import GameRepository
        assert isinstance(repo, GameRepository)
        assert hasattr(repo, 'save_game') and hasattr(repo, 'get_game')

        # Проверяем, что репозиторий реально связан с хранилищем
        assert hasattr(repo, '_storage')

        print(f"   ✅ Репозиторий корректно инициализирован через DI-контейнер.")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # 4) Определён сервис для работы с репозиторием.
    # =========================================================
    print("\n4) Определён сервис для работы с репозиторием:")
    try:
        p = get_full_path('datasource/service/game_service_impl.py')
        assert container_ready

        service = container.get("service")
        from datasource.service.game_service_impl import GameServiceImplWithRepo
        from domain.service.interface import GameServiceInterface

        assert isinstance(service, GameServiceImplWithRepo)
        assert isinstance(service, GameServiceInterface), "Сервис не реализует интерфейс domain-слоя"

        # Проверяем инъекцию репозитория
        assert hasattr(service, '_repo')

        print(f"   ✅ Сервис корректно инициализирован, принимает репозиторий и реализует интерфейс.")
        print(f"   📁 Путь: {p}")
        passed += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # =========================================================
    # ИТОГ
    # =========================================================
    print("\n" + "=" * 85)
    if passed == total:
        print(f"🎉 Все {total} пункта чек-листа пройдены!")
        print("✅ Задание 5 (di-слой) выполнено полностью.")
        return True
    else:
        print(f"⚠️  Пройдено: {passed} из {total}")
        print("❌ Проверь ошибки выше")
        return False


if __name__ == "__main__":
    success = test_di_checklist()
    exit(0 if success else 1)