#!/usr/bin/env python3

import subprocess
import time
import sys
import socket
from pathlib import Path

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    try:
        result = subprocess.run(
            f"lsof -ti:{port}",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            pids = result.stdout.strip().split()
            for pid in pids:
                subprocess.run(f"kill -9 {pid}", shell=True)
            time.sleep(1)
    except Exception:
        pass

def run_in_background(name, command):
    return subprocess.Popen(
        command,
        shell=True,
        stdout=sys.stdout,
        stderr=subprocess.STDOUT,
        start_new_session=True
    )

def main():
    base_dir = Path(__file__).parent
    processes = []
    
    kill_process_on_port(5555)
    kill_process_on_port(8001)
    
    if is_port_in_use(5555):
        zmq_port = 5556
    else:
        zmq_port = 5555
    
    if is_port_in_use(8001):
        web_port = 8002
    else:
        web_port = 8001
    
    try:
        zmq_proc = run_in_background(
            f"ZMQ Server порт {zmq_port}",
            f"cd {base_dir} && python3 zmq_server.py --port {zmq_port}"
        )
        processes.append(("ZMQ Server", zmq_proc, zmq_port))
        time.sleep(2)
        
        web_proc = run_in_background(
            f"Веб-сервер порт {web_port}",
            f"cd {base_dir} && python3 web_server.py --port {web_port}"
        )
        processes.append(("Веб-сервер", web_proc, web_port))
        time.sleep(3)
        
        while True:
            time.sleep(5)
            
    except KeyboardInterrupt:
        for name, proc, port in processes:
            if proc:
                proc.terminate()
                proc.wait()
        print(" Все серверы остановлены")
        
    except Exception as e:
        print(f" Ошибка: {e}")
        for _, proc, _ in processes:
            if proc:
                proc.terminate()

if __name__ == "__main__":
    main()