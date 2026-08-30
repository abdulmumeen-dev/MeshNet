"""
Network Discovery Module
Finds other MeshNet devices on your network
"""

import socket
import json
import time
import uuid
import threading

class Discovery:
    def __init__(self):
        self.node_id = str(uuid.uuid4())[:8]
        self.port = 9876
        self.nodes = {}
        self.running = True
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def broadcast_discovery(self):
        message = {
            "type": "DISCOVER",
            "node_id": self.node_id,
            "timestamp": time.time(),
            "ip": self.get_local_ip()
        }
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)
        
        try:
            message_json = json.dumps(message).encode()
            sock.sendto(message_json, ('255.255.255.255', self.port))
        except Exception as e:
            print(f"Broadcast error: {e}")
        finally:
            sock.close()
    
    def listen_for_nodes(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.port))
        sock.settimeout(1)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message['node_id'] != self.node_id:
                    self.nodes[message['node_id']] = {
                        'ip': addr[0],
                        'last_seen': time.time(),
                        'node_id': message['node_id']
                    }
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
                
        sock.close()
    
    def run_scan(self, seconds=5):
        print(f"🔍 Scanning for {seconds} seconds...")
        
        self.running = True
        listener_thread = threading.Thread(target=self.listen_for_nodes, daemon=True)
        listener_thread.start()
        
        for _ in range(seconds):
            if not self.running:
                break
            self.broadcast_discovery()
            time.sleep(1)
        
        self.running = False
        return self.nodes
    
    def run(self):
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📡 IP: {self.get_local_ip()}")
        
        listener_thread = threading.Thread(target=self.listen_for_nodes, daemon=True)
        listener_thread.start()
        
        try:
            while self.running:
                self.broadcast_discovery()
                time.sleep(5)
        except KeyboardInterrupt:
            self.running = False

if __name__ == "__main__":
    discovery = Discovery()
    discovery.run()
