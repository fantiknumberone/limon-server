import asyncio
import websockets
import json
from datetime import datetime
from database import save_point, init_db

async def handler(websocket):
    print("📱 Android подключился")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await save_point(data)
                
                time = datetime.now().strftime("%H:%M:%S")
                if data.get('latitude'):
                    signal = data.get('signal', 'N/A')
                    print(f"[{time}] 📍 Сигнал: {signal} dBm")
                else:
                    print(f"[{time}] 📡 Данные без координат")
                    
            except json.JSONDecodeError:
                print(f"⚠ Не JSON: {message[:50]}...")
                
    except websockets.ConnectionClosed:
        print("📱 Android отключился")

async def main():
    await init_db()
    print("🚀 WebSocket сервер: ws://0.0.0.0:8000")
    print("📊 Лимит: 10 000 точек (автоочистка)")
    
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())