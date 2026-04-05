#!/usr/bin/env python3
r"""
Скрипт проверки Задания 4 (web-слой) через реальные HTTP-запросы.
✅ Запуск: из корня проекта
   cd ~/Рабочий\ стол/PY-3_H
   python src/verify_http.py
"""
import os
import sys
import json
import uuid
import time
import socket
import subprocess
import signal
import atexit
import urllib.request
import urllib.error

# === НАСТРОЙКА ПУТЕЙ ===
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# === КОНСТАНТЫ ===
BASE_URL = "http://127.0.0.1:5000"
HOST, PORT = "127.0.0.1", 5000
TIMEOUT = 10

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
server_process = None


def cleanup_server():
    """Корректно останавливает тестовый сервер."""
    global server_process
    if server_process and server_process.poll() is None:
        print("\n🛑 Остановка тестового сервера...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()


atexit.register(cleanup_server)


def is_port_in_use(host: str, port: int) -> bool:
    """Проверяет, занят ли порт."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def kill_process_on_port(port: int):
    """Пытается убить процесс, занимающий порт (Linux)."""
    try:
        result = subprocess.run(
            f"lsof -ti :{port}",
            shell=True, capture_output=True, text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"⚠️  Порт {port} занят PID {pid}. Завершаем...")
                os.kill(int(pid), signal.SIGTERM)
            time.sleep(1)
    except Exception:
        pass


def wait_for_server(max_attempts: int = 30, delay: float = 0.5) -> bool:
    """Ждёт, пока сервер начнёт принимать соединения на порт."""
    for i in range(max_attempts):
        if not is_port_in_use(HOST, PORT):
            time.sleep(delay)
            continue
        return True
    return False


def start_server():
    """Запускает Flask-сервер."""
    global server_process
    
    if is_port_in_use(HOST, PORT):
        print(f"⚠️  Порт {PORT} уже занят. Пытаемся освободить...")
        kill_process_on_port(PORT)
        if is_port_in_use(HOST, PORT):
            print(f"❌ Не удалось освободить порт {PORT}.")
            print(f"   1) Останови другие процессы: kill -9 $(lsof -ti :{PORT})")
            print(f"   2) Или запусти сервер вручную в другом терминале:")
            print(f"      cd {src_dir} && python main.py")
            print(f"   3) Затем перезапусти этот скрипт.")
            sys.exit(1)
    
    print("🚀 Запуск тестового сервера...")
    python_exe = sys.executable
    main_path = os.path.join(src_dir, "main.py")
    
    server_process = subprocess.Popen(
        [python_exe, main_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=src_dir,
        text=True,
        start_new_session=True
    )
    
    if not wait_for_server():
        print("❌ Сервер не ответил за 15 секунд.")
        if server_process.poll() is None:
            server_process.terminate()
            out, _ = server_process.communicate(timeout=2)
            if out:
                print("📋 Лог сервера:")
                print(out)
        raise RuntimeError("Сервер не запустился.")
    
    print(f"✅ Сервер запущен: {BASE_URL}")


def send_request(url: str, method: str = "POST", data: dict = None, headers: dict = None) -> tuple[int, dict | None]:
    """Отправляет HTTP-запрос и возвращает (статус, ответ)."""
    if headers is None:
        headers = {}
    if data is not None and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    else:
        body = data.encode("utf-8") if isinstance(data, str) else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
            return resp.status, response_data
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            return e.code, error_data
        except:
            return e.code, {"error": e.reason}
    except Exception as e:
        return -1, {"error": str(e)}


def count_non_zero(matrix: list) -> int:
    """Считает количество непустых клеток в матрице."""
    return sum(1 for row in matrix for cell in row if cell != 0)


def check_checklist():
    """Проверяет пункты 4.3, 4.4, 4.5 через запросы."""
    print("🔍 Проверка Задания 4 (web-слой) через HTTP-запросы...")
    print("=" * 70)
    
    passed = 0
    total = 3
    
    # ---------------------------------------------------------
    # ПУНКТ 4.3: POST /game/{UUID} работает
    # ---------------------------------------------------------
    print("\n[4.3] Контроллер с методом POST /game/{UUID}...")
    try:
        test_uuid = str(uuid.uuid4())
        payload = {
            "id": test_uuid,
            "board": {"matrix": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "size": 3}
        }
        url = f"{BASE_URL}/game/{test_uuid}"
        status, response = send_request(url, "POST", payload)
        
        assert status == 200, f"Ожидался 200, получено {status}"
        assert "board" in response and "matrix" in response["board"], "Ответ не содержит поля board/matrix"
        
        matrix = response["board"]["matrix"]
        has_computer_move = any(cell == 2 for row in matrix for cell in row)
        assert has_computer_move, "Компьютер не сделал ход (нет значения 2 в матрице)"
        
        print(f"   ✅ 4.3 — POST /game/{{UUID}} работает")
        passed += 1
    except AssertionError as e:
        print(f"   ❌ 4.3 — Ошибка проверки: {e}")
    except Exception as e:
        print(f"   ❌ 4.3 — Исключение: {type(e).__name__}: {e}")
    
    # ---------------------------------------------------------
    # ПУНКТ 4.4: Ошибка 400 при некорректных данных
    # ---------------------------------------------------------
    print("\n[4.4] Некорректная игра → ошибка 400 с описанием...")
    try:
        # Тест 1: невалидный UUID
        status1, resp1 = send_request(
            f"{BASE_URL}/game/invalid-uuid",
            "POST",
            {"id": "bad", "board": {"matrix": [[0]], "size": 1}}
        )
        assert status1 == 400, f"Невалидный UUID: ожидался 400, получено {status1}"
        assert "description" in resp1 or "error" in resp1, "Ответ 400 не содержит описания"
        
        # Тест 2: пустое тело
        status2, _ = send_request(
            f"{BASE_URL}/game/{uuid.uuid4()}",
            "POST",
            data="",
            headers={"Content-Type": "application/json"}
        )
        assert status2 == 400, f"Пустой запрос: ожидался 400, получено {status2}"
        
        print(f"   ✅ 4.4 — Некорректные запросы → 400 с описанием")
        passed += 1
    except AssertionError as e:
        print(f"   ❌ 4.4 — Ошибка проверки: {e}")
    except Exception as e:
        print(f"   ❌ 4.4 — Исключение: {type(e).__name__}: {e}")
    
    # ---------------------------------------------------------
    # ПУНКТ 4.5: Несколько игр одновременно (ИСПРАВЛЕНО)
    # ---------------------------------------------------------
    print("\n[4.5] Поддержка нескольких игр одновременно...")
    try:
        uuid_1 = str(uuid.uuid4())
        uuid_2 = str(uuid.uuid4())
        
        # === Игра 1: первый ход ===
        payload1 = {"id": uuid_1, "board": {"matrix": [[1,0,0],[0,0,0],[0,0,0]], "size": 3}}
        status1, resp1 = send_request(f"{BASE_URL}/game/{uuid_1}", "POST", payload1)
        assert status1 == 200, f"Игра 1, ход 1: ожидался 200, получено {status1}"
        assert "board" in resp1 and "matrix" in resp1["board"]
        matrix1_after_first = resp1["board"]["matrix"]
        count1_after_first = count_non_zero(matrix1_after_first)
        print(f"      [4.5] Игра 1: после 1-го хода непустых клеток = {count1_after_first}")
        
        # === Игра 2: независимый первый ход ===
        payload2 = {"id": uuid_2, "board": {"matrix": [[0,0,0],[0,2,0],[0,0,0]], "size": 3}}
        status2, resp2 = send_request(f"{BASE_URL}/game/{uuid_2}", "POST", payload2)
        assert status2 == 200, f"Игра 2, ход 1: ожидался 200, получено {status2}"
        assert "board" in resp2 and "matrix" in resp2["board"]
        matrix2_after_first = resp2["board"]["matrix"]
        count2_after_first = count_non_zero(matrix2_after_first)
        print(f"      [4.5] Игра 2: после 1-го хода непустых клеток = {count2_after_first}")
        
        # === Игра 1: ВТОРОЙ ХОД (продолжение) ===
        # 🔥 ИСПРАВЛЕНО: отправляем board как объект {matrix: ..., size: ...}, а не просто матрицу
        payload1_cont = {
            "id": uuid_1,
            "board": {
                "matrix": matrix1_after_first,  # состояние после ответа сервера
                "size": 3
            }
        }
        status1_cont, resp1_cont = send_request(f"{BASE_URL}/game/{uuid_1}", "POST", payload1_cont)
        assert status1_cont == 200, f"Игра 1, ход 2: ожидался 200, получено {status1_cont}"
        assert "board" in resp1_cont and "matrix" in resp1_cont["board"]
        
        matrix1_after_second = resp1_cont["board"]["matrix"]
        count1_after_second = count_non_zero(matrix1_after_second)
        print(f"      [4.5] Игра 1: после 2-го хода непустых клеток = {count1_after_second}")
        
        # === Проверка изоляции ===
        # В игре 1 должно быть больше ходов, чем в игре 2 (потому что мы сделали ей 2 хода, а игре 2 — только 1)
        assert count1_after_second > count2_after_first, \
            f"Игры не изолированы: игра 1 имеет {count1_after_second} ходов, игра 2 — {count2_after_first}"
        
        # Дополнительно: проверяем, что UUID в ответе совпадает с запрошенным
        assert resp1_cont.get("id") == uuid_1, "UUID в ответе не совпадает с запрошенным"
        
        print(f"   ✅ 4.5 — Параллельные игры с изоляцией по UUID")
        passed += 1
        
    except AssertionError as e:
        msg = str(e) if str(e) else "Проверка не прошла (пустое сообщение assert)"
        print(f"   ❌ 4.5 — Ошибка проверки: {msg}")
        # Печатаем отладочную информацию
        print(f"      💡 Подсказка: проверь, что сервер сохраняет состояние между запросами по UUID")
    except KeyError as e:
        print(f"   ❌ 4.5 — Ошибка структуры ответа: ключ {e} не найден в JSON")
        print(f"      💡 Проверь, что контроллер возвращает {{'board': {{'matrix': ..., 'size': ...}}, 'id': ...}}")
    except Exception as e:
        print(f"   ❌ 4.5 — Исключение: {type(e).__name__}: {e}")
        import traceback
        print(f"      🔍 Трассировка: {traceback.format_exc()[:200]}")
    
    # ---------------------------------------------------------
    # ИТОГ
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    if passed == total:
        print(f"🎉 Все {total} сетевых пункта чек-листа пройдены!")
        print("✅ Задание 4 (web-слой) функционально работает.")
        print("\n📋 Сводка:")
        print("   ✅ 4.3 — POST /game/{UUID} работает")
        print("   ✅ 4.4 — Некорректные запросы → 400 с описанием")
        print("   ✅ 4.5 — Параллельные игры изолированы")
        return True
    else:
        print(f"⚠️  Пройдено: {passed} из {total}")
        if passed < total:
            print("❌ Проверь ошибки выше. Чаще всего проблема в формате JSON или сохранении состояния.")
        return False


if __name__ == "__main__":
    try:
        start_server()
        success = check_checklist()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
        exit(130)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        exit(1)