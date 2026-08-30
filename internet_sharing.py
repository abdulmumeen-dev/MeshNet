"""
Internet Sharing Module
Share internet between devices
"""

import socket
import json
import threading
import time
import uuid
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class InternetSharing:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.gateway_port = 8080
        self.has_internet = self.check_internet()
        self.nodes = {}
        self.running = True
        
    def check_internet(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            try:
                import urllib.request
                urllib.request.urlopen("http://www.google.com", timeout=3)
                return True
            except:
                return False
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def proxy_request(self, client_socket, request_data):
        try:
            request_str = request_data.decode()
            lines = request_str.split('\n')
            if not lines:
                return
            
            first_line = lines[0].split()
            if len(first_line) < 2:
                return
            
            url = first_line[1]
            
            if url.startswith('http://') and HAS_REQUESTS:
                response = self.fetch_http(url)
                client_socket.send(response)
            elif url.startswith('https://'):
                client_socket.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
            else:
                client_socket.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                
        except Exception as e:
            print(f"Proxy error: {e}")
            client_socket.send(f"HTTP/1.1 500 Error: {e}\r\n\r\n".encode())
        
        client_socket.close()
    
    def fetch_http(self, url):
        if not HAS_REQUESTS:
            return b"HTTP/1.1 500 Error: requests not installed\r\n\r\n"
        
        try:
            response = requests.get(url, timeout=5)
            status_line = f"HTTP/1.1 {response.status_code} OK\r\n"
            headers = ""
            for key, value in response.headers.items():
                headers += f"{key}: {value}\r\n"
            body = response.content
            return f"{status_line}{headers}\r\n".encode() + body
        except Exception as e:
            return f"HTTP/1.1 500 Error: {e}\r\n\r\n".encode()
    
    def handle_gateway_client(self, client_socket, addr):
        try:
            data = client_socket.recv(4096)
            if data:
                try:
                    json_data = json.loads(data.decode())
                    if json_data.get('type') == 'register':
                        node_id = json_data.get('node_id')
                        self.nodes[node_id] = {
                            'ip': addr[0],
                            'registered': time.time()
                        }
                        client_socket.send(json.dumps({
                            'status': 'registered',
                            'gateway': self.node_id
                        }).encode())
                        print(f"🔗 Node {node_id[:8]} registered")
                except:
                    self.proxy_request(client_socket, data)
                    
        except Exception as e:
            print(f"Gateway error: {e}")
        finally:
            client_socket.close()
    
    def start_gateway_server(self):
        if not self.has_internet:
            print("❌ No internet!")
            return
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', self.gateway_port))
        server.listen(10)
        server.settimeout(1)
        
        print(f"🌐 Gateway on port {self.gateway_port}")
        print(f"📡 IP: {self.get_local_ip()}")
        
        while self.running:
            try:
                client, addr = server.accept()
                threading.Thread(
                    target=self.handle_gateway_client,
                    args=(client, addr),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Server error: {e}")
        
        server.close()
    
    def connect_to_gateway(self, gateway_ip: str):
        if self.has_internet:
            print("⚠️ Already have internet!")
            return None
        
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((gateway_ip, self.gateway_port))
            
            registration = {
                "type": "register",
                "node_id": self.node_id
            }
            client.send(json.dumps(registration).encode())
            
            response = json.loads(client.recv(1024).decode())
            if response.get('status') == 'registered':
                print(f"✅ Connected to gateway {gateway_ip}")
                return client
            else:
                print(f"❌ Registration failed")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None
    
    def browse(self, client_socket, url: str):
        if not client_socket:
            print("❌ Not connected")
            return
        
        try:
            request = f"GET {url} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
            client_socket.send(request.encode())
            
            response = client_socket.recv(8192)
            if response:
                print(f"📨 Response received:")
                print(response[:500].decode())
                return response
                
        except Exception as e:
            print(f"❌ Browse error: {e}")
    
    def run(self, mode: str = "auto", gateway_ip: Optional[str] = None):
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📶 Internet: {'Yes' if self.has_internet else 'No'}")
        
        if mode == "auto":
            mode = "gateway" if self.has_internet else "client"
        
        if mode == "gateway":
            if not self.has_internet:
                print("❌ Cannot be gateway!")
                return
            
            gateway_thread = threading.Thread(target=self.start_gateway_server, daemon=True)
            gateway_thread.start()
            
            print("🌍 Gateway active!")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
            
        else:
            if not gateway_ip:
                print("❌ Need gateway IP!")
                return
            
            client = self.connect_to_gateway(gateway_ip)
            if not client:
                return
            
            print("\n💻 Browse the internet!")
            try:
                while True:
                    url = input("🌐 URL: ")
                    if url.lower() == 'quit':
                        break
                    if not url.startswith('http'):
                        url = 'http://' + url
                    self.browse(client, url)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
            
            client.close()

if __name__ == "__main__":
    import sys
    node_id = str(uuid.uuid4())[:8]
    sharing = InternetSharing(node_id)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "gateway":
            sharing.run(mode="gateway")
        elif sys.argv[1] == "client" and len(sys.argv) > 2:
            sharing.run(mode="client", gateway_ip=sys.argv[2])
    else:
        sharing.run()
