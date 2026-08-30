"""
Auto-Discovery Module
Continuously monitors for gateways
"""

import socket
import json
import threading
import time
import uuid
from typing import Optional

class AutoDiscovery:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.port = 9876
        self.gateway_port = 9878
        self.running = True
        self.gateways = {}
        self.connected_gateway = None
        self.callbacks = []
        
    def start(self):
        print("🔄 Auto-Discovery started")
        
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()
        
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
        
    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.port))
        sock.settimeout(1)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message['node_id'] != self.node_id:
                    node_ip = addr[0]
                    node_id = message['node_id']
                    
                    if self._is_gateway(node_ip):
                        if node_id not in self.gateways:
                            self.gateways[node_id] = {
                                'ip': node_ip,
                                'discovered': time.time(),
                                'node_id': node_id
                            }
                            print(f"🎯 Gateway found: {node_id[:8]} at {node_ip}")
                            
                            for callback in self.callbacks:
                                try:
                                    callback(node_ip, node_id)
                                except:
                                    pass
                                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
                
        sock.close()
    
    def _is_gateway(self, ip: str) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, self.gateway_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _monitor(self):
        while self.running:
            time.sleep(10)
            
            dead = []
            for node_id, info in self.gateways.items():
                if not self._is_gateway(info['ip']):
                    dead.append(node_id)
            
            for node_id in dead:
                print(f"⚠️ Gateway {node_id[:8]} offline")
                del self.gateways[node_id]
    
    def on_gateway_found(self, callback):
        self.callbacks.append(callback)
    
    def stop(self):
        self.running = False
        print("🔄 Auto-Discovery stopped")
