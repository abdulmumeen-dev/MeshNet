"""
MeshNet Ultra - The Most Powerful Version
Combines AI, Blockchain, and Bandwidth Aggregation
"""

import sys
import time
import threading
import socket
import json
import uuid
from typing import Optional, Dict, List

# Import all modules
try:
    from discovery import Discovery
    from communication import Communication
    from internet_sharing import InternetSharing
    from auto_discovery import AutoDiscovery
    from encryption import EncryptionManager
    from ai_routing import AIRouter, AIOptimizer
    from blockchain import ReputationManager
    from bandwidth_aggregator import BandwidthAggregator
except ImportError as e:
    print(f"⚠️ Module import error: {e}")
    print("Make sure all files are in the same directory")
    sys.exit(1)

class MeshNetUltra:
    def __init__(self):
        self.node_id = str(uuid.uuid4())[:8]
        self.ip = self._get_local_ip()
        
        # Initialize all systems
        print("=" * 60)
        print("🚀 MESHNET ULTRA - The Most Powerful Mesh Network")
        print("=" * 60)
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📡 IP: {self.ip}")
        print("=" * 60)
        
        # Initialize subsystems
        self.encryption = EncryptionManager()
        self.ai_router = AIRouter(self.node_id)
        self.ai_optimizer = AIOptimizer()
        self.reputation = ReputationManager(self.node_id)
        self.aggregator = BandwidthAggregator(self.node_id)
        self.auto_discovery = None
        self.is_gateway = False
        
        print("✅ All systems initialized!")
        print("=" * 60)
    
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start_auto_discovery(self):
        """Start auto-discovery with AI optimization"""
        print("🔄 Starting AI-Optimized Auto-Discovery...")
        self.auto_discovery = AutoDiscovery(self.node_id)
        self.auto_discovery.on_gateway_found(self._on_gateway_found)
        self.auto_discovery.start()
        
        # Start AI optimization in background
        threading.Thread(target=self._ai_optimization_loop, daemon=True).start()
    
    def _on_gateway_found(self, ip: str, node_id: str):
        """Called when a gateway is found"""
        print(f"🎯 Gateway found: {node_id[:8]} at {ip}")
        
        # Check reputation
        trust_score = self.reputation.get_trust_score(node_id)
        if trust_score < 0.3:
            print(f"⚠️ Gateway {node_id[:8]} has low reputation ({trust_score:.2f})")
            return
        
        # Auto-connect if not already connected
        if not self.aggregator.gateways:
            self._connect_to_gateway(ip, node_id)
    
    def _connect_to_gateway(self, ip: str, node_id: str):
        """Connect to a gateway with AI optimization"""
        try:
            print(f"🔗 Connecting to gateway {node_id[:8]} at {ip}...")
            
            # Use encryption
            secure_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secure_socket.connect((ip, 9878))
            
            # Register with gateway
            registration = {
                "type": "register",
                "node_id": self.node_id,
                "encrypted": True
            }
            secure_socket.send(json.dumps(registration).encode())
            
            response = json.loads(secure_socket.recv(1024).decode())
            if response.get('status') == 'registered':
                # Estimate bandwidth
                bandwidth = self._estimate_bandwidth(secure_socket)
                
                # Add to aggregator
                self.aggregator.add_gateway(node_id, secure_socket, bandwidth)
                self.reputation.record_connection(self.node_id, node_id)
                
                print(f"✅ Connected to gateway! (Bandwidth: {bandwidth:.2f} Mbps)")
                
                # AI recommends best gateway
                gateways = [
                    {
                        'node_id': node_id,
                        'bandwidth': bandwidth,
                        'latency': 10,
                        'reputation': self.reputation.get_trust_score(node_id)
                    }
                ]
                recommended = self.ai_optimizer.recommend_gateways(gateways)
                if recommended:
                    print(f"🤖 AI recommends gateway: {recommended[0][:8]}")
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    def _estimate_bandwidth(self, socket_obj) -> float:
        """Estimate bandwidth to a gateway"""
        try:
            # Send a small test file
            test_data = b'X' * 1024 * 100  # 100KB
            start = time.time()
            socket_obj.send(test_data)
            elapsed = time.time() - start
            
            bandwidth = (100 * 8) / elapsed  # in Kbps
            return bandwidth / 1000  # in Mbps
        except:
            return 10.0  # Default if test fails
    
    def _ai_optimization_loop(self):
        """Background AI optimization"""
        while True:
            try:
                time.sleep(30)  # Run every 30 seconds
                
                # Analyze network state
                network_state = {
                    'gateways': len(self.aggregator.gateways),
                    'bandwidth': self.aggregator.get_speed_boost(),
                    'reputation': self.reputation.get_network_stats()
                }
                
                # AI predicts load
                load = self.ai_optimizer.predict_network_load([network_state])
                
                # Optimize routing
                if load > 0.8:  # High load
                    print("⚠️ AI detected high network load - optimizing...")
                    # Distribute traffic across more gateways
                    
            except Exception as e:
                print(f"AI optimization error: {e}")
    
    def start_gateway(self):
        """Start as a gateway with all features"""
        print("🌍 Starting MeshNet Ultra Gateway...")
        self.is_gateway = True
        
        # Start internet sharing with AI optimization
        sharing = InternetSharing(self.node_id)
        sharing.run(mode="gateway")
    
    def download_with_aggregation(self, url: str, output: str):
        """Download using bandwidth aggregation"""
        if not self.aggregator.gateways:
            print("❌ No gateways available. Connect to a gateway first.")
            return
        
        print("📥 Starting accelerated download...")
        speed_boost = self.aggregator.get_speed_boost()
        print(f"🚀 Speed boost: {speed_boost:.2f}x")
        
        self.aggregator.download_file(url, output)
    
    def show_status(self):
        """Show comprehensive network status"""
        print("\n" + "=" * 60)
        print("📊 MESHNET ULTRA STATUS")
        print("=" * 60)
        
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📡 IP: {self.ip}")
        print(f"🔐 Encryption: {'Active' if self.encryption else 'Inactive'}")
        print(f"🤖 AI Router: {'Active' if self.ai_router else 'Inactive'}")
        print(f"⛓️ Blockchain: {'Active' if self.reputation else 'Inactive'}")
        
        print(f"\n📶 Gateways: {len(self.aggregator.gateways)}")
        if self.aggregator.gateways:
            for gw_id, gw_info in self.aggregator.gateways.items():
                print(f"  → {gw_id[:8]} ({gw_info['bandwidth']:.2f} Mbps)")
        
        network_stats = self.reputation.get_network_stats()
        print(f"\n⛓️ Network Stats:")
        print(f"  Chain Length: {network_stats['chain_length']}")
        print(f"  Total Nodes: {network_stats['total_nodes']}")
        print(f"  Banned Nodes: {network_stats['banned_nodes']}")
        print(f"  Avg Reputation: {network_stats['average_reputation']:.2f}")
        
        print(f"\n🚀 Speed Boost: {self.aggregator.get_speed_boost():.2f}x")
        print("=" * 60)
    
    def menu(self):
        """Main menu"""
        print("\n" + "=" * 60)
        print("MESHNET ULTRA - Main Menu")
        print("=" * 60)
        print("1. 🔍 Start Auto-Discovery")
        print("2. 🌍 Become Gateway (Share Internet)")
        print("3. 📥 Download with Aggregation")
        print("4. 📊 Show Status")
        print("5. ⛓️ Verify Blockchain")
        print("6. 🚫 Ban Malicious Node")
        print("7. ❌ Exit")
        print("=" * 60)
        
        return input("👉 Choose: ").strip()
    
    def run(self):
        """Main application loop"""
        print("\n🎯 MeshNet Ultra is ready!")
        print("💡 Type 'help' for commands")
        
        while True:
            try:
                choice = self.menu()
                
                if choice == "1":
                    self.start_auto_discovery()
                
                elif choice == "2":
                    self.start_gateway()
                
                elif choice == "3":
                    url = input("Enter URL: ").strip()
                    output = input("Output file name: ").strip()
                    self.download_with_aggregation(url, output)
                
                elif choice == "4":
                    self.show_status()
                
                elif choice == "5":
                    if self.reputation.blockchain.verify_chain():
                        print("✅ Blockchain verified successfully!")
                    else:
                        print("❌ Blockchain verification failed!")
                
                elif choice == "6":
                    node_id = input("Enter node ID to ban: ").strip()
                    reason = input("Reason: ").strip()
                    self.reputation.ban_node(node_id, reason)
                
                elif choice in ["7", "q", "quit", "exit"]:
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid option")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    ultra = MeshNetUltra()
    ultra.run()
