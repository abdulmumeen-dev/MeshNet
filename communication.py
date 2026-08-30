"""
Peer-to-Peer Communication Module
Send and receive messages between devices
"""

import socket
import json
import threading
import time
import uuid
from typing import Optional

class Communication:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.port = 9877
        self.connections = {}
        self.running = True
        
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', self.port))
        server.listen(5)
        server.settimeout(1)
        
        print(f"🔊 Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client, addr),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Server error: {e}")
                
        server.close()
    
    def handle_client(self, client_socket, addr):
        try:
            data = client_socket.recv(4096)
            if data:
                message = json.loads(data.decode())
                print(f"📨 From {message.get('sender', 'unknown')}: {message.get('content', '')}")
                
                if 'sender' in message:
                    self.connections[message['sender']] = client_socket
                
                response = {"status": "received", "timestamp": time.time()}
                client_socket.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()
    
    def send_message(self, target_ip: str, content: str):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((target_ip, self.port))
            
            message = {
                "sender": self.node_id,
                "content": content,
                "timestamp": time.time()
            }
            client.send(json.dumps(message).encode())
            
            response = client.recv(1024)
            if response:
                ack = json.loads(response.decode())
                print(f"✅ Delivered! {ack}")
                
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def run(self, target_ip: Optional[str] = None):
        print(f"🆔 Node ID: {self.node_id}")
        
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        time.sleep(1)
        
        if target_ip:
            print(f"🎯 Targeting {target_ip}")
            try:
                while self.running:
                    msg = input("💬 Enter message (or 'quit'): ")
                    if msg.lower() == 'quit':
                        break
                    self.send_message(target_ip, msg)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
        else:
            print("🔍 Waiting for messages...")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
        
        self.running = False

if __name__ == "__main__":
    import sys
    node_id = str(uuid.uuid4())[:8]
    comm = Communication(node_id)
    
    if len(sys.argv) > 1:
        comm.run(target_ip=sys.argv[1])
    else:
        comm.run()
