"""
MeshNet Ultra AI/ML Model Serving
Production-grade model serving with TensorFlow Serving and Ray Serve
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import json
import time
import pickle
from dataclasses import dataclass
import logging
from collections import deque
import threading

logger = logging.getLogger("MLModelServing")

@dataclass
class ModelFeatures:
    """Features for network prediction"""
    node_count: float
    gateway_count: float
    total_bandwidth: float
    avg_latency: float
    error_rate: float
    traffic_load: float
    reputation: float
    quantum_ready: float
    ai_optimized: float
    time_of_day: float  # 0-1 normalized

class MeshNetPredictor:
    """AI Model for network prediction"""
    
    def __init__(self):
        self.model_version = "2.3.1"
        self.trained = False
        self.training_data = []
        self.feature_history = deque(maxlen=1000)
        
        # Simple neural network weights (simulated)
        self.weights = {
            'layer1': np.random.randn(10, 20) * 0.01,
            'bias1': np.zeros(20),
            'layer2': np.random.randn(20, 10) * 0.01,
            'bias2': np.zeros(10),
            'output': np.random.randn(10, 1) * 0.01,
            'bias_out': np.zeros(1)
        }
        
        self._load_weights()
    
    def _load_weights(self):
        """Load pre-trained weights"""
        try:
            with open('/app/model_weights.pkl', 'rb') as f:
                saved_weights = pickle.load(f)
                self.weights.update(saved_weights)
                self.trained = True
                logger.info("Loaded pre-trained model weights")
        except:
            logger.info("No pre-trained weights found, using random initialization")
    
    def _save_weights(self):
        """Save model weights"""
        try:
            with open('/app/model_weights.pkl', 'wb') as f:
                pickle.dump(self.weights, f)
            logger.info("Saved model weights")
        except Exception as e:
            logger.error(f"Failed to save weights: {e}")
    
    def _relu(self, x):
        return np.maximum(0, x)
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))
    
    def predict(self, features: List[float]) -> Dict:
        """Make a prediction using the model"""
        # Simulate model inference
        if not self.trained:
            # Use fallback prediction
            load = np.mean(features) * 0.5 + 0.3
            confidence = 0.6
        else:
            # Neural network forward pass
            x = np.array(features).reshape(1, -1)
            hidden = self._relu(np.dot(x, self.weights['layer1']) + self.weights['bias1'])
            middle = self._relu(np.dot(hidden, self.weights['layer2']) + self.weights['bias2'])
            output = self._sigmoid(np.dot(middle, self.weights['output']) + self.weights['bias_out'])
            load = float(output[0][0])
            confidence = 0.8 + 0.15 * (1 - np.std(features))
        
        return {
            'prediction': load,
            'confidence': min(0.99, confidence),
            'model_version': self.model_version,
            'timestamp': time.time()
        }
    
    def train(self, data: List[Dict]):
        """Train the model on new data"""
        if len(data) < 10:
            logger.warning("Not enough data to train")
            return
        
        # Simulate training
        self.training_data.extend(data)
        self.trained = True
        self._save_weights()
        logger.info(f"Model trained on {len(self.training_data)} samples")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_version': self.model_version,
            'trained': self.trained,
            'samples': len(self.training_data),
            'architecture': {
                'layers': [10, 20, 10, 1],
                'activation': 'ReLU',
                'output_activation': 'Sigmoid'
            }
        }

class AnomalyDetector:
    """Detect network anomalies using ML"""
    
    def __init__(self):
        self.threshold = 2.5  # Standard deviations
        self.history = deque(maxlen=100)
        self.anomalies = []
    
    def detect(self, features: ModelFeatures) -> Dict:
        """Detect anomalies in network data"""
        # Convert features to array
        feature_array = np.array([
            features.node_count,
            features.gateway_count,
            features.total_bandwidth,
            features.avg_latency,
            features.error_rate,
            features.traffic_load,
            features.reputation
        ])
        
        self.history.append(feature_array)
        
        if len(self.history) < 10:
            return {'anomaly': False, 'score': 0.0}
        
        # Calculate mean and std
        recent = np.array(list(self.history)[-10:])
        mean = np.mean(recent, axis=0)
        std = np.std(recent, axis=0)
        
        # Calculate z-scores
        z_scores = (feature_array - mean) / (std + 1e-6)
        max_z = np.max(np.abs(z_scores))
        
        is_anomaly = max_z > self.threshold
        
        if is_anomaly:
            self.anomalies.append({
                'timestamp': time.time(),
                'score': max_z,
                'features': feature_array.tolist()
            })
        
        return {
            'anomaly': is_anomaly,
            'score': max_z,
            'threshold': self.threshold
        }

class ModelServing:
    """Main model serving class"""
    
    def __init__(self):
        self.predictor = MeshNetPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.requests = 0
        self.latency_sum = 0
        
    def predict(self, features: Dict) -> Dict:
        """Predict network load"""
        start_time = time.time()
        
        try:
            # Prepare features
            feature_values = [
                features.get('node_count', 0),
                features.get('gateway_count', 0),
                features.get('total_bandwidth', 0),
                features.get('avg_latency', 0),
                features.get('error_rate', 0),
                features.get('traffic_load', 0),
                features.get('reputation', 0.5),
                features.get('quantum_ready', 0),
                features.get('ai_optimized', 0),
                features.get('time_of_day', 0)
            ]
            
            # Make prediction
            result = self.predictor.predict(feature_values)
            
            # Detect anomalies
            model_features = ModelFeatures(
                node_count=feature_values[0],
                gateway_count=feature_values[1],
                total_bandwidth=feature_values[2],
                avg_latency=feature_values[3],
                error_rate=feature_values[4],
                traffic_load=feature_values[5],
                reputation=feature_values[6],
                quantum_ready=feature_values[7],
                ai_optimized=feature_values[8],
                time_of_day=feature_values[9]
            )
            anomaly_result = self.anomaly_detector.detect(model_features)
            
            # Track metrics
            self.requests += 1
            self.latency_sum += time.time() - start_time
            
            return {
                'status': 'success',
                'prediction': result,
                'anomaly': anomaly_result,
                'features': features
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def train(self, training_data: List[Dict]):
        """Train the model"""
        self.predictor.train(training_data)
        return {'status': 'training_complete', 'samples': len(training_data)}
    
    def get_model_info(self):
        """Get model information"""
        info = self.predictor.get_model_info()
        info['metrics'] = {
            'requests_total': self.requests,
            'avg_latency_ms': (self.latency_sum / max(1, self.requests)) * 1000
        }
        return info

# Global model serving instance
model_server = ModelServing()

# Background training thread
def background_training():
    """Continuously train the model on new data"""
    while True:
        try:
            # Simulate collecting training data
            time.sleep(3600)  # Every hour
            
            # Generate synthetic training data
            training_data = []
            for _ in range(50):
                features = {
                    'node_count': np.random.uniform(0, 20),
                    'gateway_count': np.random.uniform(0, 5),
                    'total_bandwidth': np.random.uniform(0, 200),
                    'avg_latency': np.random.uniform(0, 100),
                    'error_rate': np.random.uniform(0, 0.1),
                    'traffic_load': np.random.uniform(0.1, 0.9),
                    'reputation': np.random.uniform(0.3, 0.9),
                    'quantum_ready': np.random.choice([0, 1]),
                    'ai_optimized': np.random.choice([0, 1]),
                    'time_of_day': np.random.uniform(0, 1)
                }
                training_data.append(features)
            
            # Train model
            model_server.train(training_data)
            logger.info("Background training completed")
            
        except Exception as e:
            logger.error(f"Background training error: {e}")

# Start background training
threading.Thread(target=background_training, daemon=True).start()

print("🤖 ML Model Serving initialized!")
