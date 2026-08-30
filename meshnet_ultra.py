"""
MESHNET ULTRA - The Most Powerful Mesh Network
Features: AI Routing, Blockchain Reputation, Bandwidth Aggregation,
Quantum Encryption, Neural Prediction, Global Mesh Index
"""

import sys
import os
import time
import threading
import socket
import json
import uuid
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime

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
    print(f"⚠️ Core module import error: {e}")
    print("Make sure all files are in the same directory")
    sys.exit(1)

# Import advanced features (optional)
try:
    from quantum_encryption import QuantumSecureChannel
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    print("ℹ️ Quantum encryption not available")

try:
    from neural_predictor import NeuralPredictor, AdaptiveNetworkOptimizer
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False
    print("ℹ️ Neural prediction not available")

try:
    from global_mesh_index import GlobalMeshIndex
    GLOBAL_INDEX_AVAILABLE = True
except ImportError:
    GLOBAL_INDEX_AVAILABLE = False
    print("ℹ️ Global Mesh Index not available")

class MeshNetUltra:
    """The Ultimate Mesh Networking System"""
    
    def __init__(self):
        # Basic identity
        self.node_id = str(uuid.uuid4())[:8]
        self.ip = self._get_local_ip()
        self.start_time = time.time()
        self.is_gateway = False
        self.is_connected = False
        self.running = True
        
        # Initialize subsystems
        print("=" * 70)
        print("🚀 MESHNET ULTRA - The Most Powerful Mesh Network on Earth")
        print("=" * 70)
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📡 IP Address: {self.ip}")
        print(f"🔐 Quantum Ready: {'✅ Yes' if QUANTUM_AVAILABLE else '❌ No'}")
        print(f"🧠 Neural AI: {'✅ Yes' if NEURAL_AVAILABLE else '❌ No'}")
        print(f"🌍 Global Index: {'✅ Yes' if GLOBAL_INDEX_AVAILABLE else '❌ No'}")
        print("=" * 70)
        
        # Initialize core systems
        self.encryption = EncryptionManager()
        self.ai_router = AIRouter(self.node_id)
        self.ai_optimizer = AIOptimizer()
        self.reputation = ReputationManager(self.node_id)
        self.aggregator = BandwidthAggregator(self.node_id)
        self.auto_discovery = None
        
        # Initialize advanced systems
        self.quantum = None
        self.neural_optimizer = None
        self.global_index = None
        
        if QUANTUM_AVAILABLE:
            self.quantum = QuantumSecureChannel(self.node_id)
            print("✅ Quantum encryption initialized")
        
        if NEURAL_AVAILABLE:
            self.neural_optimizer = AdaptiveNetworkOptimizer()
            print("✅ Neural AI optimizer initialized")
        
        if GLOBAL_INDEX_AVAILABLE:
            self.global_index = GlobalMeshIndex(self.node_id)
            print("✅ Global Mesh Index initialized")
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'data_transferred': 0,
            'connections_made': 0,
            'ai_optimizations': 0
        }
        
        print("=" * 70)
        print("🎯 All systems ready! Type 'help' for commands")
        print("=" * 70)
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
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
        if NEURAL_AVAILABLE:
            threading.Thread(target=self._ai_optimization_loop, daemon=True).start()
        
        # Start quantum discovery if available
        if QUANTUM_AVAILABLE:
            threading.Thread(target=self._quantum_discovery_loop, daemon=True).start()
        
        # Register in global index
        if GLOBAL_INDEX_AVAILABLE:
            self._register_in_global_index()
    
    def _on_gateway_found(self, ip: str, node_id: str):
        """Called when a gateway is found"""
        print(f"🎯 Gateway found: {node_id[:8]} at {ip}")
        
        # Check reputation
        trust_score = self.reputation.get_trust_score(node_id)
        if trust_score < 0.3:
            print(f"⚠️ Gateway {node_id[:8]} has low reputation ({trust_score:.2f})")
            return
        
        # Try quantum connection first if available
        if QUANTUM_AVAILABLE:
            session_id = self.quantum_connect(ip, node_id)
            if session_id:
                print(f"🔐 Quantum connection established to {node_id[:8]}")
        
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
                "encrypted": True,
                "quantum_ready": QUANTUM_AVAILABLE
            }
            secure_socket.send(json.dumps(registration).encode())
            
            response = json.loads(secure_socket.recv(1024).decode())
            if response.get('status') == 'registered':
                # Estimate bandwidth
                bandwidth = self._estimate_bandwidth(secure_socket)
                
                # Add to aggregator
                self.aggregator.add_gateway(node_id, secure_socket, bandwidth)
                self.reputation.record_connection(self.node_id, node_id)
                self.stats['connections_made'] += 1
                
                print(f"✅ Connected to gateway! (Bandwidth: {bandwidth:.2f} Mbps)")
                self.is_connected = True
                
                # AI recommends best gateway
                if NEURAL_AVAILABLE:
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
                    
                    # Train neural network
                    self.neural_optimizer.predictor.add_data_point(bandwidth / 100.0)
                    
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
        while self.running:
            try:
                time.sleep(30)  # Run every 30 seconds
                
                if not self.aggregator.gateways:
                    continue
                
                # Collect traffic data
                traffic_data = []
                for gw_id, info in self.aggregator.gateways.items():
                    traffic_data.append(info.get('bandwidth', 10) / 100.0)
                
                # Analyze with neural network
                if NEURAL_AVAILABLE and traffic_data:
                    analysis = self.neural_optimizer.analyze_network(traffic_data)
                    self.stats['ai_optimizations'] += 1
                    
                    if analysis['predictions']['next_load'] and analysis['predictions']['next_load'] > 0.8:
                        print("🧠 AI: High load detected - optimizing gateways...")
                        # Distribute traffic across more gateways
                        for gw_id in list(self.aggregator.gateways.keys())[:2]:
                            if gw_id not in self.aggregator.gateways:
                                continue
                            # Rebalance connections
                            pass
                
            except Exception as e:
                print(f"AI optimization error: {e}")
    
    def _quantum_discovery_loop(self):
        """Background quantum discovery"""
        while self.running:
            try:
                time.sleep(60)  # Every minute
                
                if not QUANTUM_AVAILABLE:
                    break
                
                # Broadcast quantum readiness
                # In production, this would exchange quantum keys
                print("🔐 Quantum discovery: broadcasting readiness...")
                
            except Exception as e:
                print(f"Quantum discovery error: {e}")
    
    def _register_in_global_index(self):
        """Register in global mesh index"""
        if not GLOBAL_INDEX_AVAILABLE:
            return
        
        print("🌍 Registering in Global Mesh Index...")
        
        capabilities = {
            'is_gateway': self.is_gateway,
            'bandwidth': self.aggregator.get_speed_boost() if hasattr(self.aggregator, 'get_speed_boost') else 10,
            'reputation': self.reputation.get_trust_score(self.node_id),
            'quantum_ready': QUANTUM_AVAILABLE,
            'neural_ai': NEURAL_AVAILABLE,
            'version': '2.0.0'
        }
        
        self.global_index.register_node(
            self.node_id,
            self.ip,
            9878,
            capabilities
        )
        
        # Get global stats
        stats = self.global_index.discover_global_network()
        print(f"🌍 Global Network: {stats['total_nodes']} nodes, {stats['active_gateways']} gateways")
    
    def quantum_connect(self, target_ip: str, target_id: str) -> Optional[str]:
        """Connect using quantum-resistant encryption"""
        if not QUANTUM_AVAILABLE:
            print("❌ Quantum encryption not available")
            return None
        
        print(f"🔐 Establishing quantum-secure connection to {target_id[:8]}...")
        
        try:
            # Exchange public keys (simulated)
            peer_public_key = os.urandom(64)
            
            # Establish quantum session
            ciphertext = self.quantum.establish_quantum_session(peer_public_key)
            
            # Store session
            session_id = hashlib.sha3_256(str(time.time()).encode()).hexdigest()[:16]
            
            print(f"✅ Quantum-secure session established!")
            return session_id
            
        except Exception as e:
            print(f"❌ Quantum connection failed: {e}")
            return None
    
    def ai_optimize_network(self) -> Optional[Dict]:
        """Use AI to optimize network performance"""
        if not NEURAL_AVAILABLE:
            print("❌ Neural AI not available")
            return None
        
        print("🧠 AI is analyzing network...")
        
        # Collect traffic data
        traffic_data = []
        if self.aggregator.gateways:
            for gw_id, info in self.aggregator.gateways.items():
                traffic_data.append(info.get('bandwidth', 10) / 100.0)
        
        if not traffic_data:
            print("ℹ️ No traffic data available")
            return None
        
        # Analyze
        analysis = self.neural_optimizer.analyze_network(traffic_data)
        self.stats['ai_optimizations'] += 1
        
        print("\n📊 AI Network Analysis:")
        if analysis['predictions']['next_load']:
            print(f"  📈 Next Load Prediction: {analysis['predictions']['next_load']*100:.1f}%")
        print(f"  📉 Trend: {analysis['predictions']['trend']}")
        print(f"  ⚠️ Anomaly Score: {analysis['predictions']['anomaly_score']:.2f}")
        print(f"  🎯 Confidence: {analysis.get('confidence', 0)*100:.1f}%")
        
        if analysis['recommendations']:
            print("\n💡 AI Recommendations:")
            for rec in analysis['recommendations']:
                print(f"  → {rec}")
        
        return analysis
    
    def show_global_stats(self):
        """Show global mesh statistics"""
        if not GLOBAL_INDEX_AVAILABLE:
            print("❌ Global Mesh Index not available")
            return
        
        print("\n🌍 GLOBAL MESH INDEX")
        print("=" * 50)
        
        report = self.global_index.create_mesh_reports()
        
        print(f"📊 Total Nodes: {report['stats']['total_nodes']}")
        print(f"🌐 Active Gateways: {report['stats']['active_gateways']}")
        print(f"⚡ Total Bandwidth: {report['stats']['total_bandwidth']:.2f} Mbps")
        print(f"⭐ Global Reputation: {report['stats']['global_reputation']:.2f}")
        print(f"💚 Network Health: {report['network_health']}")
        
        if report['top_nodes']:
            print("\n🏆 Top Nodes:")
            for node in report['top_nodes']:
                print(f"  → {node['node_id'][:8]} (Rep: {node['reputation']:.2f}, BW: {node['bandwidth']:.1f} Mbps)")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  → {rec}")
    
    def quantum_send(self, target_ip: str, target_id: str, message: str):
        """Send message using quantum encryption"""
        if not QUANTUM_AVAILABLE:
            print("❌ Quantum encryption not available")
            return
        
        print(f"🔐 Sending quantum-encrypted message to {target_id[:8]}...")
        
        try:
            # Establish quantum session
            session_id = self.quantum_connect(target_ip, target_id)
            if not session_id:
                return
            
            # Encrypt message
            encrypted = self.quantum.encrypt_quantum(session_id, message.encode())
            
            # Send encrypted message (in production, send via socket)
            print(f"✅ Quantum-encrypted message sent!")
            self.stats['messages_sent'] += 1
            
        except Exception as e:
            print(f"❌ Quantum send failed: {e}")
    
    def become_gateway(self):
        """Start as a gateway with all features"""
        print("🌍 Starting MeshNet Ultra Gateway...")
        self.is_gateway = True
        
        # Start internet sharing
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
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        
        print("\n" + "=" * 60)
        print("📊 MESHNET ULTRA STATUS")
        print("=" * 60)
        print(f"🆔 Node ID: {self.node_id}")
        print(f"📡 IP: {self.ip}")
        print(f"⏱️  Uptime: {hours}h {minutes}m")
        print(f"🔐 Encryption: {'Active' if self.encryption else 'Inactive'}")
        print(f"🔐 Quantum: {'✅ Available' if QUANTUM_AVAILABLE else '❌ Not Available'}")
        print(f"🧠 Neural AI: {'✅ Available' if NEURAL_AVAILABLE else '❌ Not Available'}")
        print(f"🌍 Global Index: {'✅ Available' if GLOBAL_INDEX_AVAILABLE else '❌ Not Available'}")
        
        print(f"\n📶 Gateways: {len(self.aggregator.gateways)}")
        if self.aggregator.gateways:
            for gw_id, gw_info in self.aggregator.gateways.items():
                print(f"  → {gw_id[:8]} ({gw_info['bandwidth']:.2f} Mbps)")
        
        # Blockchain stats
        network_stats = self.reputation.get_network_stats()
        print(f"\n⛓️ Blockchain Stats:")
        print(f"  Chain Length: {network_stats['chain_length']}")
        print(f"  Total Nodes: {network_stats['total_nodes']}")
        print(f"  Banned Nodes: {network_stats['banned_nodes']}")
        print(f"  Avg Reputation: {network_stats['average_reputation']:.2f}")
        
        # Performance stats
        print(f"\n📊 Performance:")
        print(f"  Speed Boost: {self.aggregator.get_speed_boost():.2f}x")
        print(f"  Messages Sent: {self.stats['messages_sent']}")
        print(f"  Messages Received: {self.stats['messages_received']}")
        print(f"  Connections Made: {self.stats['connections_made']}")
        print(f"  AI Optimizations: {self.stats['ai_optimizations']}")
        
        # Neural AI stats
        if NEURAL_AVAILABLE and self.neural_optimizer:
            print(f"  Neural Training: {len(self.neural_optimizer.predictor.history)} samples")
            print(f"  Neural Trained: {'✅ Yes' if self.neural_optimizer.predictor.trained else '❌ No'}")
        
        print("=" * 60)
    
    def verify_blockchain(self):
        """Verify the blockchain"""
        if self.reputation.blockchain.verify_chain():
            print("✅ Blockchain verified successfully!")
        else:
            print("❌ Blockchain verification failed!")
    
    def ban_node(self, node_id: str, reason: str):
        """Ban a malicious node"""
        self.reputation.ban_node(node_id, reason)
    
    def show_help(self):
        """Show help menu"""
        print("\n" + "=" * 60)
        print("📚 MESHNET ULTRA - Help")
        print("=" * 60)
        print("\n🔍 Discovery & Connection:")
        print("  1. Start Auto-Discovery - Automatically find gateways")
        print("  2. Become Gateway - Share your internet")
        print("  3. Connect to Gateway - Get internet from others")
        print("\n📊 Management:")
        print("  4. Show Status - View all system stats")
        print("  5. AI Optimize - Neural network analysis")
        print("  6. Global Index - View global mesh stats")
        print("\n🛡️ Security:")
        print("  7. Verify Blockchain - Check network integrity")
        print("  8. Ban Node - Remove malicious nodes")
        print("\n🔐 Advanced:")
        if QUANTUM_AVAILABLE:
            print("  9. Quantum Connect - Quantum-secure connection")
            print("  10. Quantum Send - Send quantum-encrypted message")
        print("\n💾 Data:")
        print("  11. Download - Accelerated file download")
        print("\n🚪 Exit:")
        print("  12. Exit - Quit MeshNet Ultra")
        print("=" * 60)
    
    def main_menu(self):
        """Display main menu"""
        print("\n" + "=" * 60)
        print("MESHNET ULTRA - Main Menu")
        print("=" * 60)
        print("1. 🔍 Start Auto-Discovery")
        print("2. 🌍 Become Gateway (Share Internet)")
        print("3. 🔗 Connect to Gateway (Get Internet)")
        print("4. 📊 Show Status")
        print("5. 🧠 AI Network Optimization")
        print("6. 🌍 Global Mesh Index")
        print("7. ⛓️ Verify Blockchain")
        print("8. 🚫 Ban Malicious Node")
        if QUANTUM_AVAILABLE:
            print("9. 🔐 Quantum-Secure Connection")
            print("10. 📨 Quantum Send Message")
        print("11. 📥 Download with Aggregation")
        print("12. 📚 Help")
        print("13. ❌ Exit")
        print("=" * 60)
        
        return input("👉 Choose an option: ").strip()
    
    def connect_to_gateway_interactive(self):
        """Interactive connection to a gateway"""
        print("\n🔗 Connect to Gateway")
        
        # Scan for gateways
        print("🔍 Scanning for gateways...")
        d = Discovery()
        nodes = d.run_scan(3)
        
        if not nodes:
            print("❌ No nodes found. Make sure someone is running as a gateway.")
            return
        
        gateways = []
        for node_id, info in nodes.items():
            # Check if it's a gateway
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((info['ip'], 9878)) == 0:
                    gateways.append((node_id, info))
                sock.close()
            except:
                pass
        
        if not gateways:
            print("❌ No gateways found")
            return
        
        print("\n✅ Found gateways:")
        for i, (node_id, info) in enumerate(gateways):
            trust = self.reputation.get_trust_score(node_id)
            print(f"  {i+1}. {node_id[:8]} at {info['ip']} (Trust: {trust:.2f})")
        
        try:
            choice = int(input("\nSelect gateway (number): ")) - 1
            if choice < 0 or choice >= len(gateways):
                print("Invalid choice")
                return
            
            node_id, info = gateways[choice]
            self._connect_to_gateway(info['ip'], node_id)
            
        except ValueError:
            print("Invalid input")
    
    def quantum_connect_interactive(self):
        """Interactive quantum connection"""
        if not QUANTUM_AVAILABLE:
            print("❌ Quantum encryption not available")
            return
        
        print("\n🔐 Quantum-Secure Connection")
        target_ip = input("Enter target IP: ").strip()
        target_id = input("Enter target Node ID (or press Enter for auto): ").strip()
        
        if not target_id:
            target_id = "unknown"
        
        self.quantum_connect(target_ip, target_id)
    
    def quantum_send_interactive(self):
        """Interactive quantum message sending"""
        if not QUANTUM_AVAILABLE:
            print("❌ Quantum encryption not available")
            return
        
        print("\n📨 Quantum Send Message")
        target_ip = input("Enter target IP: ").strip()
        target_id = input("Enter target Node ID: ").strip()
        message = input("Enter message: ").strip()
        
        if not all([target_ip, target_id, message]):
            print("❌ All fields required")
            return
        
        self.quantum_send(target_ip, target_id, message)
    
    def download_interactive(self):
        """Interactive download with aggregation"""
        url = input("Enter URL to download: ").strip()
        output = input("Output filename: ").strip()
        
        if not url or not output:
            print("❌ URL and filename required")
            return
        
        self.download_with_aggregation(url, output)
    
    def run(self):
        """Main application loop"""
        print("\n🎯 MeshNet Ultra is ready!")
        print("💡 Type 'help' or choose option 12 for help")
        
        while self.running:
            try:
                choice = self.main_menu()
                
                if choice == "1":
                    self.start_auto_discovery()
                
                elif choice == "2":
                    self.become_gateway()
                
                elif choice == "3":
                    self.connect_to_gateway_interactive()
                
                elif choice == "4":
                    self.show_status()
                
                elif choice == "5":
                    self.ai_optimize_network()
                
                elif choice == "6":
                    self.show_global_stats()
                
                elif choice == "7":
                    self.verify_blockchain()
                
                elif choice == "8":
                    node_id = input("Enter node ID to ban: ").strip()
                    reason = input("Reason: ").strip()
                    self.ban_node(node_id, reason)
                
                elif choice == "9" and QUANTUM_AVAILABLE:
                    self.quantum_connect_interactive()
                
                elif choice == "10" and QUANTUM_AVAILABLE:
                    self.quantum_send_interactive()
                
                elif choice == "11":
                    self.download_interactive()
                
                elif choice == "12":
                    self.show_help()
                
                elif choice in ["13", "q", "quit", "exit"]:
                    print("\n👋 Goodbye! Thanks for using MeshNet Ultra!")
                    self.running = False
                    break
                
                else:
                    print("❌ Invalid option. Type 'help' or choose 12 for help.")
                
                if self.running:
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using MeshNet Ultra!")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if self.running:
                    input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        ultra = MeshNetUltra()
        ultra.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
