# main.py — Точка входа в приложение
from di import Container
import webbrowser
import threading
import time
import os

# Флаг чтобы браузер открылся только один раз
_browser_opened = False

def open_browser(url: str, delay: float = 2.0):
    """
    Открывает браузер с задержкой, чтобы сервер успел запуститься.
    Запускается в отдельном потоке.
    """
    global _browser_opened
    time.sleep(delay)
    
    # Проверяем, не открыли ли уже
    if _browser_opened:
        return
    
    _browser_opened = True
    try:
        webbrowser.open(url)
        print(f"🌐 Браузер открыт: {url}")
    except Exception as e:
        print(f"⚠️  Не удалось открыть браузер: {e}")
        print(f"   Открой вручную: {url}")

if __name__ == "__main__":
    # Сбрасываем флаг при каждом запуске
    _browser_opened = False
    
    # 1. Создаём контейнер
    container = Container()
    
    # 2. Получаем Flask-приложение
    app = container.get("controller")
    
    # 3. Запускаем открытие браузера в фоновом потоке
    threading.Thread(
        target=open_browser, 
        args=["http://127.0.0.1:5000/"], 
        daemon=True
    ).start()
    
    # 4. Запускаем сервер
    print("\n🚀 Сервер запущен!")
    print("📍 Адрес: http://127.0.0.1:5000")
    print("🎮 Игра откроется автоматически через 2 секунды...\n")
    
    # debug=False чтобы не было двойной перезагрузки
    app.run(host='0.0.0.0', port=5000, debug=False)