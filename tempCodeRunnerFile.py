#!/usr/bin/env python3
import subprocess
import sys
import time
import os
from pathlib import Path

def run_in_background(name, command):
    """Запуск в фоне без чтения вывода"""
    print(f"🚀 Запуск {name}...")
    
    # Для Linux/macOS
    return subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.DEVNULL,  # не читаем вывод
        stderr=subprocess.DEVNULL,
        start_new_session=True  # запуск в новой сессии
    )

def main():
    print("=" * 50)
    print("🎯 Система карты сигнала")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Проверяем установлены ли пакеты
    try:
        import jinja2
        import fastapi
        print("✅ Все пакеты установлены")
    except ImportError as e:
        print(f"❌ Не установлен пакет: {e}")
        print("📦 Установите: pip install jinja2 fastapi uvicorn websockets aiosqlite")
        return
    
    # Запускаем серверы
    processes = []
    
    try:
        # 1. WebSocket сервер
        ws_proc = run_in_background(
            "WebSocket для Android",
            f"cd {base_dir} && python3 ws_server.py"
        )
        processes.append(("WebSocket", ws_proc))
        time.sleep(2)
        
        # 2. Веб-сервер
        web_proc = run_in_background(
            "Веб-сервер",
            f"cd {base_dir} && python3 web_server.py"
        )
        processes.append(("Веб-сервер", web_proc))
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("✅ Все серверы запущены:")
        print(f"   📡 Android: ws://0.0.0.0:8000")
        print(f"   🌐 Браузер: http://localhost:8001")
        print(f"   📊 API: http://localhost:8001/api/data")
        print("\n🛑 Нажмите Ctrl+C для остановки")
        print("=" * 50)
        
        # Бесконечное ожидание
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка серверов...")
        for name, proc in processes:
            if proc:
                proc.terminate()
                print(f"⏹️ Остановлен: {name}")
        print("✅ Все серверы остановлены")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        for _, proc in processes:
            if proc:
                proc.terminate()

if __name__ == "__main__":
    main()