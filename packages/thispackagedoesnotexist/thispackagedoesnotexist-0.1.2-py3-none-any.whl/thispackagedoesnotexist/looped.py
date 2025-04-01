import http.client
import json
from wmi import WMI
import threading
import time
from typing import Callable, Dict, Any
import pythoncom

class LoopedClient:
    def __init__(self, host: str, port: int, retry: str = 'forever', retry_interval: int = 5, timeout: int = 30):
        pythoncom.CoInitialize()
        self.host = host
        self.port = port
        self.client_id = WMI().Win32_ComputerSystemProduct()[0].UUID
        self.connected = False
        self.running = False
        self.poll_thread = None
        self.events: Dict[str, list[Callable]] = {}
        self.retry = retry
        self.retry_interval = retry_interval
        self.timeout = timeout

    def on(self, event_name: str) -> Callable:
        def decorator(callback: Callable) -> Callable:
            if event_name not in self.events:
                self.events[event_name] = []
            self.events[event_name].append(callback)
            return callback
        return decorator
    
    def emit(self, event_name: str, *args: Any) -> None:
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args)
    
    def connect(self) -> bool:
        while True:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
            headers = {
                'Content-Type': 'application/json',
                'X-Client-Id': self.client_id
            }
            
            try:
                conn.request('POST', '/connect', json.dumps({}), headers)
                response = conn.getresponse()
                
                if response.status == 200:
                    self.connected = True
                    self.running = True
                    self.emit('connect', self.client_id)

                    self.poll_thread = threading.Thread(target=self._poll_server)
                    self.poll_thread.daemon = True
                    self.poll_thread.start()

                    return True
                else:
                    self.emit('error', 'Failed to connect')
                    if self.retry == "forever":
                        self.emit('retry', f"Retrying in {self.retry_interval} seconds...")
                        time.sleep(self.retry_interval)
                    else:
                        return False
                
            except Exception as e:
                self.emit('error', f"Connection error: {e}")
                if self.retry == "forever":
                    self.emit('retry', f"Retrying in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    return False
            finally:
                conn.close()

    def send_message(self, message: str) -> bool:
        if not self.connected:
            return False
        
        conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        headers = {
            'Content-Type': 'application/json',
            'X-Client-Id': self.client_id
        }
        data = {'message': message}
        
        try:
            conn.request('POST', '/message', json.dumps(data), headers)
            response = conn.getresponse()
            
            if response.status == 200:
                self.emit('message_sent', message)
                return True
            elif response.status == 403:
                return False
            else:
                self.emit('error', 'Failed to send message')
                return False
                
        except Exception as e:
            self.emit('error', f"Send error: {e}")
            return False
        finally:
            conn.close()
    
    def _poll_server(self):
        pythoncom.CoInitialize()
        while self.running:
            if not self.connected:
                if self.retry == "forever":
                    self.connect()
                    continue
                else:
                    return False
                
            conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
            headers = {
                'X-Client-Id': self.client_id
            }
            
            try:
                conn.request('GET', '/poll', headers=headers)
                response = conn.getresponse()
                
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    messages = data.get('messages', [])
                    for message in messages:
                        self.emit('message', message)
                elif response.status == 403:
                    self.connect()
            
            except Exception as e:
                self.emit('error', f"Polling error: {e}")
                self.connected = False
            finally:
                conn.close()
                time.sleep(0.1)
    
    def disconnect(self):
        self.running = False
        self.connected = False
        self.emit('disconnect')
