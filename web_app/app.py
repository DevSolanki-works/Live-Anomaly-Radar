import sys
import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# Ensure we can import our custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_stream.generator import generate_transaction
from ml_model.detector import AnomalyDetector

app = Flask(__name__)

# --- FIX: Switched async_mode to 'threading' for Windows stability ---
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize the ML Brain
detector = AnomalyDetector()

# Global stats tracker
stats = {
    "total_monitored": 0,
    "fraud_detected": 0,
    "revenue_saved": 0.0
}

# --- Database Initialization ---
def init_db():
    """Creates the SQLite database and table if it doesn't exist."""
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id TEXT PRIMARY KEY, amount REAL, method TEXT, is_anomaly BOOLEAN, score REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# --- Combined Feedback & Retraining Endpoint ---
@app.route('/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    transaction_id = data.get('id')
    is_fraud = data.get('is_fraud')
    amount = float(data.get('amount', 0))
    method = data.get('method')
    
    # 1. Update Global Stats for the Dashboard
    if is_fraud:
        stats["fraud_detected"] += 1
        stats["revenue_saved"] += amount
    
    # 2. Update the Database with human validation
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute("UPDATE transactions SET is_anomaly = ? WHERE id = ?", (is_fraud, transaction_id))
    conn.commit()
    conn.close()
    
    # 3. Retrain the Machine Learning Model
    detector.update_model(amount, method, is_fraud)
    
    # Return updated stats so the UI updates the counters
    return jsonify({
        "status": "success", 
        "stats": stats
    })

def stream_and_detect():
    print("🛰️  Radar System Online.")
    while True:
        tx = generate_transaction()
        result = detector.process_transaction(tx)
        
        if result:
            # NEW: If we are warming up, send progress to a specific socket event
            if result.get("status") == "warming_up":
                socketio.emit('warmup_update', {
                    "progress": (result['current'] / result['total']) * 100,
                    "current": result['current'],
                    "total": result['total']
                })
            
            # If training just finished
            elif result.get("status") == "trained":
                socketio.emit('warmup_finished')

            # Standard transaction processing (result will be the dict from prediction phase)
            elif "is_anomaly" in result:
                stats["total_monitored"] += 1
                # ... (save to DB and emit 'new_transaction' as usual) ...
                socketio.emit('new_transaction', result)
        
        socketio.sleep(0.5 if not detector.is_trained else 2.5) # Speed up warm-up, slow down for live

@socketio.on('connect')
def handle_connect():
    print("💻 Client connected to Radar.")
    # Threading mode handles background tasks automatically
    socketio.start_background_task(stream_and_detect)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # host '0.0.0.0' is required for Docker and Cloud deployment
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
