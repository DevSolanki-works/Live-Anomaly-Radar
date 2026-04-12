import sys, os, sqlite3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_stream.generator import generate_transaction
from ml_model.detector import AnomalyDetector

app = Flask(__name__)
# threading mode is most stable for simple deployments
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

detector = AnomalyDetector()
stats = {"total_monitored": 0, "fraud_detected": 0, "revenue_saved": 0.0}

def init_db():
    conn = sqlite3.connect('radar.db')
    conn.execute('CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, amount REAL, method TEXT, is_anomaly BOOLEAN, score REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    is_fraud = data.get('is_fraud')
    amount = float(data.get('amount', 0))
    if is_fraud:
        stats["fraud_detected"] += 1
        stats["revenue_saved"] += amount
    detector.update_model(amount, data.get('method'), is_fraud)
    return jsonify({"status": "success", "stats": stats})

def stream_and_detect():
    while True:
        tx = generate_transaction()
        res = detector.process_transaction(tx)
        
        if res["status"] == "warming_up":
            socketio.emit('warmup_update', res)
        elif res["status"] == "trained":
            socketio.emit('warmup_finished')
        else:
            stats["total_monitored"] += 1
            socketio.emit('new_transaction', res)
        
        socketio.sleep(0.4 if not detector.is_trained else 2.5)

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(stream_and_detect)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # allow_unsafe_werkzeug=True FIXES THE RENDER DEPLOYMENT ERROR
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
