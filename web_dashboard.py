"""
MeshNet Ultra Web Dashboard
Real-time network visualization and control
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import time
import threading
from datetime import datetime
import os

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store network state
network_state = {
    'nodes': {},
    'gateways': {},
    'connections': [],
    'stats': {
        'total_nodes': 0,
        'active_gateways': 0,
        'total_bandwidth': 0,
        'messages_handled': 0
    },
    'updates': []
}

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'state': network_state
    })

@app.route('/api/nodes')
def api_nodes():
    """API endpoint for nodes"""
    return jsonify(list(network_state['nodes'].values()))

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(network_state['stats'])

@app.route('/api/control', methods=['POST'])
def api_control():
    """Control endpoint"""
    data = request.json
    action = data.get('action')
    
    if action == 'discover':
        socketio.emit('control', {'action': 'discover'})
    elif action == 'gateway':
        socketio.emit('control', {'action': 'gateway'})
    elif action == 'connect':
        gateway_ip = data.get('ip')
        socketio.emit('control', {'action': 'connect', 'ip': gateway_ip})
    
    return jsonify({'status': 'ok', 'action': action})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'ok'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to updates"""
    print(f"Client {request.sid} subscribed to: {data}")

def update_network_state(new_state):
    """Update network state and broadcast"""
    global network_state
    network_state.update(new_state)
    socketio.emit('state_update', new_state)

def background_updater():
    """Background thread for updates"""
    while True:
        # Simulate network updates
        # In production, this would read from the actual mesh
        timestamp = datetime.now().isoformat()
        
        update = {
            'timestamp': timestamp,
            'state': network_state
        }
        
        socketio.emit('update', update)
        time.sleep(5)

# Start background updater
threading.Thread(target=background_updater, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=False)
