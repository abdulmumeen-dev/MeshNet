"""
Bandwidth Aggregation Module
Combine multiple connections for faster speeds
"""

import threading
import time
import socket
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os

class BandwidthAggregator:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.gateways = {}
        self.active_connections = []
        self.chunk_size = 8192
        self.max_workers = 10
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
    def add_gateway(self, gateway_id: str, connection, bandwidth: float):
        self.gateways[gateway_id] = {
            'connection': connection,
            'bandwidth': bandwidth,
            'active': True,
            'last_used': time.time()
        }
        print(f"📶 Added gateway {gateway_id[:8]} ({bandwidth:.2f} Mbps)")
    
    def remove_gateway(self, gateway_id: str):
        if gateway_id in self.gateways:
            self.gateways[gateway_id]['active'] = False
            del self.gateways[gateway_id]
            print(f"📶 Removed gateway {gateway_id[:8]}")
    
    def download_file(self, url: str, output_file: str) -> bool:
        print(f"📥 Downloading {url} using {len(self.gateways)} gateways...")
        
        if not self.gateways:
            print("❌ No gateways available!")
            return False
        
        file_info = self._get_file_info(url)
        if not file_info:
            print("❌ Failed to get file info")
            return False
        
        total_size = file_info['size']
        chunks = self._split_into_chunks(total_size, len(self.gateways))
        
        downloaded_chunks = {}
        futures = []
        
        for gateway_id, gateway_info in self.gateways.items():
            if not gateway_info['active']:
                continue
            
            gateway_chunks = []
            for i, chunk in enumerate(chunks):
                if i % len(self.gateways) == len(gateway_chunks):
                    gateway_chunks.append(chunk)
            
            future = self.executor.submit(
                self._download_chunks,
                gateway_id,
                gateway_info,
                url,
                gateway_chunks
            )
            futures.append((gateway_id, future))
        
        for gateway_id, future in futures:
            try:
                result = future.result(timeout=60)
                if result:
                    downloaded_chunks.update(result)
            except Exception as e:
                print(f"⚠️ Gateway {gateway_id[:8]} failed: {e}")
        
        if self._reassemble_file(downloaded_chunks, output_file):
            print(f"✅ File downloaded: {output_file}")
            return True
        
        print("❌ Failed to reassemble file")
        return False
    
    def _get_file_info(self, url: str) -> Optional[Dict]:
        try:
            gateway_id = list(self.gateways.keys())[0]
            conn = self.gateways[gateway_id]['connection']
            
            request = f"HEAD {url} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
            conn.send(request.encode())
            
            response = conn.recv(8192)
            if response:
                headers = response.decode().split('\n')
                for header in headers:
                    if 'Content-Length:' in header:
                        size = int(header.split(':')[1].strip())
                        return {'size': size, 'url': url}
            
            return {'size': 1048576, 'url': url}
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def _split_into_chunks(self, total_size: int, num_chunks: int) -> List[Dict]:
        chunks = []
        chunk_size = total_size // max(num_chunks, 1)
        
        for i in range(max(num_chunks, 1)):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < num_chunks - 1 else total_size
            chunks.append({
                'index': i,
                'start': start,
                'end': end,
                'size': end - start
            })
        
        return chunks
    
    def _download_chunks(self, gateway_id: str, gateway_info: Dict, url: str, chunks: List[Dict]) -> Dict:
        downloaded = {}
        conn = gateway_info['connection']
        
        for chunk in chunks:
            try:
                request = f"GET {url} HTTP/1.1\r\nHost: {url}\r\nRange: bytes={chunk['start']}-{chunk['end']}\r\nConnection: close\r\n\r\n"
                conn.send(request.encode())
                
                response = b''
                while len(response) < chunk['size']:
                    data = conn.recv(self.chunk_size)
                    if not data:
                        break
                    response += data
                
                downloaded[chunk['index']] = response
                
            except Exception as e:
                print(f"⚠️ Chunk {chunk['index']} failed: {e}")
        
        return downloaded
    
    def _reassemble_file(self, chunks: Dict, output_file: str) -> bool:
        try:
            with open(output_file, 'wb') as f:
                for i in sorted(chunks.keys()):
                    f.write(chunks[i])
            return True
        except Exception as e:
            print(f"Reassembly error: {e}")
            return False
    
    def get_speed_boost(self) -> float:
        """Calculate speed boost factor"""
        if len(self.gateways) <= 1:
            return 1.0
        
        total_bandwidth = sum(g['bandwidth'] for g in self.gateways.values())
        primary_bandwidth = list(self.gateways.values())[0]['bandwidth']
        
        return total_bandwidth / primary_bandwidth if primary_bandwidth > 0 else 1.0
