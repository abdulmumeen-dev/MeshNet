"""
Global Mesh Index (GMI)
Decentralized registry of all mesh nodes worldwide
Uses DHT (Distributed Hash Table) for discovery
"""

import hashlib
import json
import time
import socket
import threading
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class DHTNode:
    """Distributed Hash Table node"""
    
    def __init__(self, node_id: str, ip: str, port: int = 9000):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.routing_table = defaultdict(list)
        self.data_store = {}
        self.peers = set()
        self.bootstrap_nodes = [
            ("meshnet.global", 9000),
            ("bootstrap.meshnet", 9000),
        ]
        
    def get_node_id_hash(self, node_id: str) -> str:
        """Hash node ID for DHT"""
        return hashlib.sha3_256(node_id.encode()).hexdigest()
    
    def store_value(self, key: str, value: Dict) -> bool:
        """Store value in DHT"""
        key_hash = self.get_node_id_hash(key)
        self.data_store[key_hash] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': time.time() + 3600  # 1 hour TTL
        }
        return True
    
    def lookup_value(self, key: str) -> Optional[Dict]:
        """Lookup value in DHT"""
        key_hash = self.get_node_id_hash(key)
        
        if key_hash in self.data_store:
            entry = self.data_store[key_hash]
            if entry['ttl'] > time.time():
                return entry['value']
            else:
                del self.data_store[key_hash]
        
        return None
    
    def find_node(self, node_id: str) -> Optional[Tuple[str, int]]:
        """Find a node in the DHT"""
        # Check local routing table
        key_hash = self.get_node_id_hash(node_id)
        
        # Find closest known node
        closest = None
        closest_distance = float('inf')
        
        for peer in self.peers:
            peer_hash = self.get_node_id_hash(peer[0])
            distance = self._xor_distance(key_hash, peer_hash)
            
            if distance < closest_distance:
                closest = peer
                closest_distance = distance
        
        return closest
    
    def _xor_distance(self, a: str, b: str) -> int:
        """Calculate XOR distance between two hashes"""
        # Convert hex strings to ints
        a_int = int(a, 16)
        b_int = int(b, 16)
        return a_int ^ b_int
    
    def broadcast_mesh_info(self, mesh_info: Dict):
        """Broadcast mesh information to peers"""
        # Store locally first
        self.store_value(f"mesh_{self.node_id}", mesh_info)
        
        # Broadcast to peers
        for peer in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((peer[0], peer[1]))
                
                message = {
                    'type': 'DHT_STORE',
                    'key': f"mesh_{self.node_id}",
                    'value': mesh_info
                }
                sock.send(json.dumps(message).encode())
                sock.close()
            except:
                pass

class GlobalMeshIndex:
    """Global registry of all mesh nodes"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.dht = DHTNode(node_id, "0.0.0.0")
        self.mesh_nodes = {}
        self.network_stats = {
            'total_nodes': 0,
            'active_gateways': 0,
            'total_bandwidth': 0,
            'global_reputation': 0.5
        }
        
    def register_node(self, node_id: str, ip: str, port: int, capabilities: Dict):
        """Register a node in the global index"""
        mesh_info = {
            'node_id': node_id,
            'ip': ip,
            'port': port,
            'capabilities': capabilities,
            'timestamp': time.time()
        }
        
        # Store in DHT
        self.dht.store_value(f"node_{node_id}", mesh_info)
        self.mesh_nodes[node_id] = mesh_info
        
        # Update stats
        self.network_stats['total_nodes'] = len(self.mesh_nodes)
        if capabilities.get('is_gateway', False):
            self.network_stats['active_gateways'] += 1
        
        print(f"🌍 Node {node_id[:8]} registered in Global Mesh Index")
    
    def find_node_globally(self, node_id: str) -> Optional[Dict]:
        """Find a node anywhere in the world"""
        # Check DHT
        mesh_info = self.dht.lookup_value(f"node_{node_id}")
        if mesh_info:
            return mesh_info
        
        # Try to find through DHT routing
        result = self.dht.find_node(node_id)
        if result:
            # Query the peer
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((result[0], result[1]))
                
                query = {
                    'type': 'DHT_FIND',
                    'node_id': node_id
                }
                sock.send(json.dumps(query).encode())
                response = json.loads(sock.recv(1024).decode())
                sock.close()
                
                if response.get('found', False):
                    return response.get('node_info')
            except:
                pass
        
        return None
    
    def discover_global_network(self) -> Dict:
        """Discover global network statistics"""
        # Aggregate stats from all known nodes
        total_bandwidth = 0
        total_reputation = 0
        gateways = 0
        
        for node_id, info in self.mesh_nodes.items():
            caps = info.get('capabilities', {})
            if caps.get('bandwidth', 0) > 0:
                total_bandwidth += caps['bandwidth']
            if caps.get('reputation', 0.5) > 0:
                total_reputation += caps['reputation']
            if caps.get('is_gateway', False):
                gateways += 1
        
        self.network_stats = {
            'total_nodes': len(self.mesh_nodes),
            'active_gateways': gateways,
            'total_bandwidth': total_bandwidth,
            'global_reputation': total_reputation / max(1, len(self.mesh_nodes))
        }
        
        return self.network_stats
    
    def create_mesh_reports(self) -> Dict:
        """Generate global mesh reports"""
        stats = self.discover_global_network()
        
        return {
            'timestamp': time.time(),
            'stats': stats,
            'top_nodes': self._get_top_nodes(5),
            'network_health': self._assess_network_health(),
            'recommendations': self._generate_recommendations()
        }
    
    def _get_top_nodes(self, n: int) -> List[Dict]:
        """Get top N nodes by reputation"""
        nodes = []
        for node_id, info in self.mesh_nodes.items():
            nodes.append({
                'node_id': node_id,
                'reputation': info.get('capabilities', {}).get('reputation', 0.5),
                'bandwidth': info.get('capabilities', {}).get('bandwidth', 0)
            })
        
        nodes.sort(key=lambda x: x['reputation'], reverse=True)
        return nodes[:n]
    
    def _assess_network_health(self) -> str:
        """Assess overall network health"""
        stats = self.network_stats
        
        if stats['total_nodes'] < 2:
            return "⚠️ Isolated - Need more nodes"
        elif stats['active_gateways'] < 1:
            return "⚠️ No active gateways"
        elif stats['global_reputation'] > 0.7:
            return "✅ Healthy - High trust network"
        else:
            return "🔄 Stable - Moderate trust"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate network recommendations"""
        recommendations = []
        stats = self.network_stats
        
        if stats['total_nodes'] < 5:
            recommendations.append("Invite more nodes to join the mesh")
        
        if stats['active_gateways'] < 2:
            recommendations.append("Encourage more nodes to become gateways")
        
        if stats['global_reputation'] < 0.5:
            recommendations.append("Increase trust by sharing more bandwidth")
        
        if stats['total_bandwidth'] < 10:
            recommendations.append("Add faster connections to improve bandwidth")
        
        return recommendations

print("🌍 Global Mesh Index initialized!")
