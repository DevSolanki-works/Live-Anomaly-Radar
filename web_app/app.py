import sys
import os
import sqlite3
from flask import Flask, render_template, request, jsonify
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

# --- NEW: Database Initialization ---
def init_db():
    """Creates the SQLite database and table if it doesn't exist."""
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id TEXT PRIMARY KEY, amount REAL, method TEXT, is_anomaly BOOLEAN, score REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db() # Run this when the server starts

@app.route('/')
def index():
    return render_template('index.html')

def stream_and_detect():
    """Background task that generates data, runs ML, and saves to DB."""
    print("🛰️  Radar System Online. Broadcasting and Logging...")
    while True:
        tx = generate_transaction()
        result = detector.process_transaction(tx)
        
        if result:
            # --- NEW: Save to Database ---
            conn = sqlite3.connect('radar.db')
            c = conn.cursor()
            c.execute("INSERT INTO transactions (id, amount, method, is_anomaly, score) VALUES (?, ?, ?, ?, ?)",
                      (result['transaction_id'], result['amount'], result['payment_method'], result['is_anomaly'], result['anomaly_score']))
            conn.commit()
            conn.close()

            # Broadcast to frontend
            socketio.emit('new_transaction', result)
        
        socketio.sleep(2.5)

@socketio.on('connect')
def handle_connect():
    print("💻 Client connected to Radar.")
    socketio.start_background_task(stream_and_detect)

# --- NEW: Human-in-the-Loop Feedback Endpoint ---
@app.route('/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    transaction_id = data.get('id')
    is_fraud = data.get('is_fraud')
    amount = data.get('amount')
    method = data.get('method')
    
    # 1. Update the Database with human validation
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute("UPDATE transactions SET is_anomaly = ? WHERE id = ?", (is_fraud, transaction_id))
    conn.commit()
    conn.close()
    
    # 2. Retrain the Machine Learning Model
    detector.update_model(amount, method, is_fraud)
    
    return jsonify({"status": "success", "message": "Model retrained"})

if __name__ == '__main__':
    # Use the port assigned by the cloud provider, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    # Set debug=False for production to prevent security leaks
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

