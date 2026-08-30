"""
AI-Powered Routing Engine
Uses machine learning to optimize network paths
"""

import numpy as np
import time
import json
import threading
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import random

class AIRouter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.routing_table = {}
        self.latency_history = defaultdict(list)
        self.bandwidth_history = defaultdict(list)
        self.node_reputation = defaultdict(float)
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        self.weights = {
            'latency': -0.6,
            'bandwidth': 0.8,
            'hops': -0.4,
            'reputation': 0.7
        }
        
    def predict_path_score(self, path: List[str]) -> float:
        if len(path) < 2:
            return 0.0
        
        avg_latency = self._calculate_path_latency(path)
        total_bandwidth = self._calculate_path_bandwidth(path)
        hops = len(path)
        avg_reputation = self._calculate_path_reputation(path)
        
        norm_latency = 1.0 / (1.0 + avg_latency) if avg_latency > 0 else 0
        norm_bandwidth = min(total_bandwidth / 100, 1.0) if total_bandwidth > 0 else 0
        norm_hops = 1.0 / hops if hops > 0 else 0
        
        score = (
            self.weights['latency'] * norm_latency +
            self.weights['bandwidth'] * norm_bandwidth +
            self.weights['hops'] * norm_hops +
            self.weights['reputation'] * avg_reputation
        )
        
        return score
    
    def find_optimal_path(self, source: str, destination: str, known_nodes: Dict) -> List[str]:
        possible_paths = []
        
        for node_id, node_info in known_nodes.items():
            if node_id == destination:
                direct_path = [source, destination]
                score = self.predict_path_score(direct_path)
                possible_paths.append((direct_path, score))
            else:
                for dest_id in known_nodes:
                    if dest_id != node_id and dest_id != source:
                        path = [source, node_id, dest_id]
                        if dest_id == destination:
                            score = self.predict_path_score(path)
                            possible_paths.append((path, score))
        
        possible_paths.sort(key=lambda x: x[1], reverse=True)
        
        if random.random() < self.exploration_rate and len(possible_paths) > 1:
            return possible_paths[random.randint(1, min(3, len(possible_paths)-1))][0]
        
        if possible_paths:
            return possible_paths[0][0]
        return [source, destination]
    
    def update_weights(self, path: List[str], success: bool, latency: float, bandwidth: float):
        if success:
            for key in self.weights:
                if key == 'latency':
                    self.weights[key] += self.learning_rate * (1.0 / (1.0 + latency))
                elif key == 'bandwidth':
                    self.weights[key] += self.learning_rate * bandwidth
                elif key == 'reputation':
                    self.weights[key] += self.learning_rate * 0.1
        else:
            for key in self.weights:
                self.weights[key] -= self.learning_rate * 0.1
        
        for key in self.weights:
            self.weights[key] = max(-1.0, min(1.0, self.weights[key]))
    
    def _calculate_path_latency(self, path: List[str]) -> float:
        latencies = []
        for node in path:
            if node in self.latency_history:
                latencies.append(np.mean(self.latency_history[node]))
        return np.mean(latencies) if latencies else 50.0
    
    def _calculate_path_bandwidth(self, path: List[str]) -> float:
        bandwidths = []
        for node in path:
            if node in self.bandwidth_history:
                bandwidths.append(np.mean(self.bandwidth_history[node]))
        return np.sum(bandwidths) if bandwidths else 10.0
    
    def _calculate_path_reputation(self, path: List[str]) -> float:
        reps = []
        for node in path:
            if node in self.node_reputation:
                reps.append(self.node_reputation[node])
        return np.mean(reps) if reps else 0.5

class AIOptimizer:
    def __init__(self):
        self.network_state = {}
        self.prediction_model = self._init_model()
        
    def _init_model(self):
        return {
            'weights': {
                'traffic_load': 0.5,
                'node_count': -0.3,
                'avg_latency': -0.4
            }
        }
    
    def predict_network_load(self, historical_data: List[Dict]) -> float:
        if not historical_data:
            return 0.5
        
        loads = [data.get('load', 0.5) for data in historical_data[-10:]]
        if len(loads) > 1:
            x = list(range(len(loads)))
            slope = self._calculate_slope(x, loads)
            next_load = loads[-1] + slope
            return max(0.0, min(1.0, next_load))
        return loads[-1] if loads else 0.5
    
    def _calculate_slope(self, x, y):
        n = len(x)
        if n < 2:
            return 0
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x) ** 2 for xi in x)
        return numerator / denominator if denominator != 0 else 0
    
    def recommend_gateways(self, gateways: List[Dict]) -> List[str]:
        scored = []
        for gw in gateways:
            score = (
                gw.get('bandwidth', 10) * 0.4 +
                (1.0 / (1.0 + gw.get('latency', 50))) * 0.3 +
                gw.get('reputation', 0.5) * 0.3
            )
            scored.append((gw['node_id'], score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [gw_id for gw_id, _ in scored[:3]]
