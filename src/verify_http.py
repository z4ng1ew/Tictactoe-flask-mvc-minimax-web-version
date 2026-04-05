#!/usr/bin/env python3
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

src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

BASE_URL = "http://127.0.0.1:5000"
HOST, PORT = "127.0.0.1", 5000
TIMEOUT = 10

server_process = None


def cleanup_server():
    global server_process
    if server_process and server_process.poll() is None:
        print("\nОстановка тестового сервера...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()


atexit.register(cleanup_server)


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def kill_process_on_port(port: int):
    try:
        result = subprocess.run(
            f"lsof -ti :{port}",
            shell=True, capture_output=True, text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"   Порт {port} занят процессом PID {pid}. Завершаем...")
                os.kill(int(pid), signal.SIGTERM)
            time.sleep(1)
    except Exception:
        pass


def wait_for_server(max_attempts: int = 30, delay: float = 0.5) -> bool:
    for i in range(max_attempts):
        if not is_port_in_use(HOST, PORT):
            time.sleep(delay)
            continue
        return True
    return False


def start_server():
    global server_process

    if is_port_in_use(HOST, PORT):
        print(f"Порт {PORT} уже занят. Пытаемся освободить...")
        kill_process_on_port(PORT)
        if is_port_in_use(HOST, PORT):
            print(f"ОШИБКА: Не удалось освободить порт {PORT}.")
            print(f"   1) Останови другие процессы: kill -9 $(lsof -ti :{PORT})")
            print(f"   2) Или запусти сервер вручную: cd {src_dir} && python main.py")
            print(f"   3) Затем перезапусти этот скрипт.")
            sys.exit(1)

    print("Запуск тестового сервера...")
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
        print("ОШИБКА: Сервер не ответил за 15 секунд.")
        if server_process.poll() is None:
            server_process.terminate()
            out, _ = server_process.communicate(timeout=2)
            if out:
                print("Лог сервера:")
                print(out)
        raise RuntimeError("Сервер не запустился.")

    print(f"Сервер успешно запущен: {BASE_URL}")


def send_request(url: str, method: str = "POST", data: dict = None, headers: dict = None) -> tuple[int, dict | None]:
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
    return sum(1 for row in matrix for cell in row if cell != 0)


def check_checklist():
    print("Проверка Задания 4 (web-слой) через реальные HTTP-запросы...")
    print("=" * 70)

    passed = 0
    total = 3

    print("\n[4.3] Проверка: контроллер принимает POST /game/{UUID} и возвращает ход компьютера")
    try:
        test_uuid = str(uuid.uuid4())
        payload = {
            "id": test_uuid,
            "board": {"matrix": [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "size": 3}
        }
        status, response = send_request(f"{BASE_URL}/game/{test_uuid}", "POST", payload)

        assert status == 200, f"Ожидался код 200, получен {status}"
        assert "board" in response and "matrix" in response["board"], \
            "Ответ сервера не содержит полей board/matrix"
        assert any(cell == 2 for row in response["board"]["matrix"] for cell in row), \
            "Компьютер не сделал ход — значение 2 отсутствует в матрице"

        print("   УСПЕХ: маршрут POST /game/{UUID} работает, компьютер делает ответный ход")
        passed += 1
    except AssertionError as e:
        print(f"   ПРОВАЛ: {e}")
    except Exception as e:
        print(f"   ОШИБКА: {type(e).__name__}: {e}")

    print("\n[4.4] Проверка: некорректные запросы возвращают код 400 с описанием ошибки")
    try:
        status1, resp1 = send_request(
            f"{BASE_URL}/game/invalid-uuid",
            "POST",
            {"id": "bad", "board": {"matrix": [[0]], "size": 1}}
        )
        assert status1 == 400, f"Невалидный UUID: ожидался код 400, получен {status1}"
        assert "description" in resp1 or "error" in resp1, \
            "Ответ с кодом 400 не содержит описания ошибки"

        status2, _ = send_request(
            f"{BASE_URL}/game/{uuid.uuid4()}",
            "POST",
            data="",
            headers={"Content-Type": "application/json"}
        )
        assert status2 == 400, f"Пустое тело запроса: ожидался код 400, получен {status2}"

        print("   УСПЕХ: некорректные запросы отклоняются с кодом 400 и описанием")
        passed += 1
    except AssertionError as e:
        print(f"   ПРОВАЛ: {e}")
    except Exception as e:
        print(f"   ОШИБКА: {type(e).__name__}: {e}")

    print("\n[4.5] Проверка: несколько игр работают одновременно и не влияют друг на друга")
    try:
        uuid_1 = str(uuid.uuid4())
        uuid_2 = str(uuid.uuid4())

        status1, resp1 = send_request(
            f"{BASE_URL}/game/{uuid_1}", "POST",
            {"id": uuid_1, "board": {"matrix": [[1,0,0],[0,0,0],[0,0,0]], "size": 3}}
        )
        assert status1 == 200, f"Игра 1, ход 1: ожидался код 200, получен {status1}"
        matrix1 = resp1["board"]["matrix"]
        count1 = count_non_zero(matrix1)
        print(f"   Игра 1 после первого хода: заполнено клеток = {count1}")

        status2, resp2 = send_request(
            f"{BASE_URL}/game/{uuid_2}", "POST",
            {"id": uuid_2, "board": {"matrix": [[0,0,0],[0,2,0],[0,0,0]], "size": 3}}
        )
        assert status2 == 200, f"Игра 2, ход 1: ожидался код 200, получен {status2}"
        count2 = count_non_zero(resp2["board"]["matrix"])
        print(f"   Игра 2 после первого хода: заполнено клеток = {count2}")

        status1c, resp1c = send_request(
            f"{BASE_URL}/game/{uuid_1}", "POST",
            {"id": uuid_1, "board": {"matrix": matrix1, "size": 3}}
        )
        assert status1c == 200, f"Игра 1, ход 2: ожидался код 200, получен {status1c}"
        count1c = count_non_zero(resp1c["board"]["matrix"])
        print(f"   Игра 1 после второго хода: заполнено клеток = {count1c}")

        assert count1c > count2, \
            f"Игры не изолированы: игра 1 имеет {count1c} ходов, игра 2 — {count2}"
        assert resp1c.get("id") == uuid_1, \
            "UUID в ответе сервера не совпадает с UUID запроса"

        print("   УСПЕХ: параллельные игры изолированы — состояния не пересекаются")
        passed += 1

    except AssertionError as e:
        print(f"   ПРОВАЛ: {e}")
    except KeyError as e:
        print(f"   ОШИБКА: ключ {e} не найден в ответе сервера")
    except Exception as e:
        import traceback
        print(f"   ОШИБКА: {type(e).__name__}: {e}")
        print(f"   Трассировка: {traceback.format_exc()[:300]}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"Все {total} из {total} пунктов чек-листа пройдены успешно.")
        print("Задание 4 (web-слой) функционально работает.")
        print("   [4.3] ПРОЙДЕН: POST /game/{UUID} принимает ход и возвращает ответ")
        print("   [4.4] ПРОЙДЕН: Некорректные запросы отклоняются с кодом 400")
        print("   [4.5] ПРОЙДЕН: Параллельные игры изолированы по UUID")
        return True
    else:
        print(f"Пройдено: {passed} из {total} пунктов.")
        print("Проверь ошибки выше.")
        return False


if __name__ == "__main__":
    try:
        start_server()
        success = check_checklist()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        exit(130)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        exit(1)