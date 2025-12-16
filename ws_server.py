import asyncio
import websockets
import json
from datetime import datetime
from database import save_point, init_db

async def handler(websocket):
    """Обработчик подключений Android"""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Сохраняем в БД
                await save_point(data)
                
                # Лог
                time = datetime.now().strftime("%H:%M:%S")
                has_coords = "📍" if data.get('latitude') else "📡"
                print(f"[{time}] {has_coords} Сохранено: сигнал={data.get('signal')}")
                
            except json.JSONDecodeError:
                print(f" Не JSON: {message[:50]}...")
                
    except websockets.ConnectionClosed:
        print(" Android отключился")

async def main():
    await init_db()
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # бесконечное ожидание

if __name__ == "__main__":
    asyncio.run(main())