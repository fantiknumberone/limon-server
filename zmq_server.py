#!/usr/bin/env python3

import asyncio
import json
import zmq
import zmq.asyncio
from database import save_point, init_db
import signal
import sys
import argparse

class ZmqServer:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.context = zmq.asyncio.Context()
        self.running = False
    
    async def handle_message(self, message):
        try:
            if not message:
                return False
            
            message = message.strip()
            if not message.startswith('{') or not message.endswith('}'):
                return False
            
            data = json.loads(message)
            
            if 'timestamp' not in data or 'signal' not in data or 'latitude' not in data or 'longitude' not in data:
                return False
            
            await save_point(data)
            return True
            
        except Exception:
            return False
    
    async def run(self):
        socket = self.context.socket(zmq.PULL)
        address = f"tcp://{self.host}:{self.port}"
        
        socket.bind(address)
        print(f"ZMQ сервер запущен: {address}")
        
        self.running = True
        
        try:
            while self.running:
                try:
                    message = await socket.recv_string()
                    await self.handle_message(message)
                except Exception:
                    continue
                    
        except KeyboardInterrupt:
            pass
        finally:
            socket.close()
    
    def stop(self):
        self.running = False
        self.context.term()

async def main():
    parser = argparse.ArgumentParser(description='ZMQ Server для Android')
    parser.add_argument('--host', default='0.0.0.0', help='Хост для биндинга')
    parser.add_argument('--port', type=int, default=5555, help='Порт для биндинга')
    args = parser.parse_args()
    
    await init_db()
    
    server = ZmqServer(args.host, args.port)
    
    signal.signal(signal.SIGINT, lambda s, f: server.stop())
    signal.signal(signal.SIGTERM, lambda s, f: server.stop())
    
    try:
        await server.run()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    asyncio.run(main())