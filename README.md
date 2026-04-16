📡 Live Anomaly Radar: Hardware-Native AI Monitoring
Live Anomaly Radar is a real-time AI security system that utilizes unsupervised Machine Learning (Isolation Forest) to detect outliers in data streams.

This project evolved from a Simulated Web Dashboard to a Hardware-Integrated System Monitor that detects real-time CPU and RAM spikes on your local machine.

🚀 The Pivot: Systems Engineering vs. AI Wrappers
I moved away from the "Web Wrapper" trap (styling CSS/HTML for fake data) and focused on Systems Engineering:

- Real Metrics: Hooks directly into OS hardware via psutil.
- Zero-Latency Monitoring: Ditch the browser for a native system tray icon (pystray).
- Adaptive Intelligence: The model calibrates to your machine's unique "idle" state rather than using hardcoded thresholds.

✨ Features

🛡️ System Radar (Core Focus)
- Adaptive Calibration: Learns your system's baseline over 60 seconds before engaging monitoring.
- Rolling Window Analytics: Maintains a 10-minute history of metrics to reduce false positives.
- Background Operation: Runs in a daemon thread with an interactive system tray icon.
- Intelligent Alerts: Pushes native OS notifications (plyer) only when the model flags a statistically significant anomaly.

💻 Fraud Dashboard (Legacy MLOps)
- Live Stream: Real-time transaction visualization via WebSockets.
- Human-in-the-Loop: UI feedback loop that triggers model retraining from the browser.
- Containerized: Fully configured with Docker for cloud deployment.

📂 Project Structure
Real_system_radar/: Native background monitor & tray integration
ml_model/: Isolation Forest logic & retraining engine
web_app/: Legacy Flask dashboard (HTML/CSS/JS)
data_stream/: Simulated transaction generator
Dockerfile: Environment configuration
requirements.txt: System dependencies

🛠️ Installation & Setup

1. Clone the Repository
git clone https://github.com/DevSolanki-works/Live-Anomaly-Radar.git
cd Live-Anomaly-Radar

2. Set Up Environment
It is recommended to use a virtual environment:
python -m venv venv

On Windows:
venv\Scripts\activate

On Mac/Linux:
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Running the Radar

Option A: The System Radar (Recommended)
Runs the background hardware monitor with the tray icon and notifications.
python Real_system_radar/system_radar.py

Option B: The Web Dashboard (Legacy)
Runs the Flask server and the simulated data stream.
python web_app/app.py

🧠 Tech Stack
AI/ML: Scikit-learn (Isolation Forest), NumPy
System Integration: Psutil, Pystray, Plyer, Pillow
Web Backend: Flask, Flask-SocketIO, Eventlet
Infrastructure: Docker, Render deployment

⚠️ Render Deployment Fix
If deploying the web dashboard to Render, the application may crash with a Werkzeug RuntimeError. To fix this, ensure the socketio.run command in web_app/app.py allows the development server for deployment:

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

🛡️ Future Roadmap
[ ] Edge Deployment: Optimizing models for local ARM architecture.
[ ] Multi-Agent Swarms: AI agents that can automatically terminate anomalous processes.
[ ] Deep Logging: Historical anomaly analysis via SQLite.
