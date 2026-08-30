"""
Neural Network Traffic Predictor
Deep learning for network traffic forecasting
"""

import numpy as np
import time
import json
from collections import deque
from typing import List, Dict, Tuple

class SimpleNeuralNetwork:
    """Lightweight neural network for traffic prediction"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 20, output_size: int = 1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize weights (Xavier initialization)
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros((1, output_size))
        
        self.learning_rate = 0.01
        self.momentum = 0.9
        self.vW1 = np.zeros_like(self.W1)
        self.vb1 = np.zeros_like(self.b1)
        self.vW2 = np.zeros_like(self.W2)
        self.vb2 = np.zeros_like(self.b2)
        
    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass"""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self._relu(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self._sigmoid(self.z2)
        return self.a2
    
    def backward(self, X: np.ndarray, y: np.ndarray, output: np.ndarray):
        """Backward pass with gradient descent"""
        m = X.shape[0]
        
        # Output layer gradient
        dz2 = (output - y) * self._sigmoid_derivative(self.a2)
        dW2 = np.dot(self.a1.T, dz2) / m
        db2 = np.sum(dz2, axis=0, keepdims=True) / m
        
        # Hidden layer gradient
        dz1 = np.dot(dz2, self.W2.T) * self._relu_derivative(self.a1)
        dW1 = np.dot(X.T, dz1) / m
        db1 = np.sum(dz1, axis=0, keepdims=True) / m
        
        # Update weights with momentum
        self.vW2 = self.momentum * self.vW2 - self.learning_rate * dW2
        self.vb2 = self.momentum * self.vb2 - self.learning_rate * db2
        self.vW1 = self.momentum * self.vW1 - self.learning_rate * dW1
        self.vb1 = self.momentum * self.vb1 - self.learning_rate * db1
        
        self.W2 += self.vW2
        self.b2 += self.vb2
        self.W1 += self.vW1
        self.b1 += self.vb1
    
    def _relu(self, x):
        return np.maximum(0, x)
    
    def _relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))
    
    def _sigmoid_derivative(self, x):
        return x * (1 - x)
    
    def predict(self, X: np.ndarray) -> float:
        """Predict traffic load"""
        return float(self.forward(X.reshape(1, -1))[0][0])

class NeuralPredictor:
    """AI traffic predictor with temporal patterns"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.history = deque(maxlen=100)
        self.network = SimpleNeuralNetwork(window_size, 20, 1)
        self.trained = False
        self.training_data = []
        self.training_labels = []
        
    def add_data_point(self, load: float):
        """Add new data point to history"""
        self.history.append(load)
        
        # Auto-train if we have enough data
        if len(self.history) >= self.window_size + 1:
            self._train_on_new_data()
    
    def _train_on_new_data(self):
        """Train on the latest data"""
        if len(self.history) < self.window_size + 1:
            return
        
        # Prepare training example
        recent = list(self.history)[-self.window_size-1:]
        X = np.array(recent[:-1]).reshape(1, -1)
        y = np.array([recent[-1]])
        
        # Add to training set
        self.training_data.append(X.flatten())
        self.training_labels.append(y[0])
        
        # Keep only last 100 examples
        if len(self.training_data) > 100:
            self.training_data = self.training_data[-100:]
            self.training_labels = self.training_labels[-100:]
        
        # Train network
        if len(self.training_data) >= 10:
            X_train = np.array(self.training_data[-50:])
            y_train = np.array(self.training_labels[-50:]).reshape(-1, 1)
            
            # Train for 10 epochs
            for _ in range(10):
                output = self.network.forward(X_train)
                self.network.backward(X_train, y_train, output)
            
            self.trained = True
    
    def predict_next_load(self) -> Optional[float]:
        """Predict the next traffic load"""
        if not self.trained or len(self.history) < self.window_size:
            return None
        
        # Get recent data
        recent = list(self.history)[-self.window_size:]
        X = np.array(recent).reshape(1, -1)
        
        # Predict
        prediction = self.network.predict(X)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, prediction))
    
    def get_trend(self) -> str:
        """Get traffic trend direction"""
        if len(self.history) < 5:
            return "stable"
        
        recent = list(self.history)[-5:]
        if recent[-1] > recent[0] * 1.1:
            return "increasing"
        elif recent[-1] < recent[0] * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def get_anomaly_score(self) -> float:
        """Detect anomalies in traffic patterns"""
        if len(self.history) < 10:
            return 0.0
        
        recent = list(self.history)[-10:]
        mean = np.mean(recent)
        std = np.std(recent)
        
        if std == 0:
            return 0.0
        
        # Calculate anomaly score
        latest = recent[-1]
        z_score = abs(latest - mean) / std
        
        return min(1.0, z_score / 3.0)  # Normalize to [0, 1]

class AdaptiveNetworkOptimizer:
    """Network optimizer using neural predictions"""
    
    def __init__(self):
        self.predictor = NeuralPredictor()
        self.optimization_history = []
        self.adaptive_rate = 0.1
        
    def analyze_network(self, traffic_data: List[float]) -> Dict:
        """Analyze network and provide optimizations"""
        # Add data to predictor
        for load in traffic_data:
            self.predictor.add_data_point(load)
        
        # Get predictions
        next_load = self.predictor.predict_next_load()
        trend = self.predictor.get_trend()
        anomaly = self.predictor.get_anomaly_score()
        
        # Generate recommendations
        recommendations = []
        
        if next_load and next_load > 0.8:
            recommendations.append("High load predicted - activate load balancing")
        elif next_load and next_load < 0.2:
            recommendations.append("Low load - reduce active gateways")
        
        if anomaly > 0.7:
            recommendations.append("⚠️ Anomaly detected - investigate network")
        elif anomaly > 0.4:
            recommendations.append("Suspicious pattern - monitor closely")
        
        if trend == "increasing":
            recommendations.append("Traffic increasing - prepare for scaling")
        elif trend == "decreasing":
            recommendations.append("Traffic decreasing - optimize resource usage")
        
        return {
            'predictions': {
                'next_load': next_load,
                'trend': trend,
                'anomaly_score': anomaly
            },
            'recommendations': recommendations,
            'confidence': self._calculate_confidence()
        }
    
    def _calculate_confidence(self) -> float:
        """Calculate prediction confidence"""
        if len(self.predictor.history) < 20:
            return 0.3
        elif len(self.predictor.history) < 50:
            return 0.6
        else:
            return 0.85

print("🧠 Neural Network Predictor initialized!")
