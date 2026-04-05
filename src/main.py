from di import Container
import webbrowser
import threading
import time
import os

_browser_opened = False

def open_browser(url: str, delay: float = 2.0):

    global _browser_opened
    time.sleep(delay)
    
    if _browser_opened:
        return
    
    _browser_opened = True
    try:
        webbrowser.open(url)
        print(f" Браузер открыт: {url}")
    except Exception as e:
        print(f"  Не удалось открыть браузер: {e}")
        print(f"   Открой вручную: {url}")

if __name__ == "__main__":
    _browser_opened = False
    
    container = Container()
    
    app = container.get("controller")
    
    threading.Thread(
        target=open_browser, 
        args=["http://127.0.0.1:5000/"], 
        daemon=True
    ).start()

    print("\n Сервер запущен!")
    print(" Адрес: http://127.0.0.1:5000")
    print(" Игра откроется автоматически через 2 секунды...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)