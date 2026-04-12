import sys
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import eventlet

# Ensure we can import our custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_stream.generator import generate_transaction
from ml_model.detector import AnomalyDetector

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize the ML Brain
detector = AnomalyDetector()

@app.route('/')
def index():
    return render_template('index.html')

def stream_and_detect():
    """Background task that generates data and runs ML detection."""
    print("🛰️  Radar System Online. Broadcasting to WebSocket...")
    while True:
        # 1. Get transaction from generator
        tx = generate_transaction()
        
        # 2. Process via ML Model
        result = detector.process_transaction(tx)
        
        # 3. If model is out of warm-up, send to frontend
        if result:
            socketio.emit('new_transaction', result)
        
        # Control the flow speed (adjust for drama!)
        socketio.sleep(0.8)

# Start the background stream when the first client connects
@socketio.on('connect')
def handle_connect():
    print("💻 Client connected to Radar.")
    socketio.start_background_task(stream_and_detect)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
