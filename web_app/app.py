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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

detector = AnomalyDetector()

# Global stats tracker for the Command Center
stats = {
    "total_monitored": 0,
    "fraud_detected": 0,
    "revenue_saved": 0.0
}

def init_db():
    """Creates the SQLite database for permanent logging."""
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

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Receives clicks from the UI and updates stats/model."""
    data = request.json
    transaction_id = data.get('id')
    is_fraud = data.get('is_fraud')
    amount = float(data.get('amount', 0))
    method = data.get('method')
    
    # 1. Update Global Stats
    if is_fraud:
        stats["fraud_detected"] += 1
        stats["revenue_saved"] += amount
    
    # 2. Update DB
    conn = sqlite3.connect('radar.db')
    c = conn.cursor()
    c.execute("UPDATE transactions SET is_anomaly = ? WHERE id = ?", (is_fraud, transaction_id))
    conn.commit()
    conn.close()
    
    # 3. Retrain Brain
    detector.update_model(amount, method, is_fraud)
    
    return jsonify({"status": "success", "stats": stats})

def stream_and_detect():
    """The main loop generating data and emitting to UI."""
    print("🛰️ Radar System Online.")
    while True:
        tx = generate_transaction()
        res = detector.process_transaction(tx)
        
        if res["status"] == "warming_up":
            socketio.emit('warmup_update', res)
        
        elif res["status"] == "trained":
            socketio.emit('warmup_finished')
            
        elif res["status"] == "live":
            stats["total_monitored"] += 1
            
            # Log to DB
            conn = sqlite3.connect('radar.db')
            c = conn.cursor()
            c.execute("INSERT INTO transactions (id, amount, method, is_anomaly, score) VALUES (?, ?, ?, ?, ?)",
                      (res['transaction_id'], res['amount'], res['payment_method'], res['is_anomaly'], res['anomaly_score']))
            conn.commit()
            conn.close()

            socketio.emit('new_transaction', res)
        
        # Fast during warmup, slow during live viewing
        socketio.sleep(0.4 if not detector.is_trained else 2.5)

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(stream_and_detect)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # allow_unsafe_werkzeug=True fixes the Render crash
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
