# AI Anomaly Radar: Real-Time Fraud Detection System

An end-to-end MLOps application that simulates live e-commerce traffic, detects anomalies using unsupervised machine learning, and allows for real-time "Human-in-the-Loop" model retraining.

## 🚀 The Architecture
This project bridges the gap between static ML notebooks and production-grade software engineering.

- **Data Generation:** Custom Python engine simulating asynchronous transaction streams.
- **ML Engine:** Unsupervised **Isolation Forest** (Scikit-Learn) with a 50-transaction "warm-up" phase.
- **Backend:** Flask & WebSockets (Socket.IO) for real-time, low-latency data broadcasting.
- **Frontend:** Dark-mode OLED dashboard with live data visualization via **Chart.js**.
- **Storage:** SQLite database for logging every transaction and its anomaly score.
- **DevOps:** Fully containerized using **Docker** for cross-platform portability.

## 🧠 Key Learning Features
- **Active Learning:** Built an interface to provide feedback to the model, triggering instant retraining on the server.
- **Streaming Data:** Handled live data flow using Eventlet and WebSockets instead of traditional HTTP polling.
- **Unsupervised Learning:** Implemented anomaly detection without pre-labeled datasets, mirroring real-world fraud scenarios.

## 🛠️ Installation & Run
1. `docker build -t ai-radar .`
2. `docker run -p 5000:5000 ai-radar`
3. Visit `localhost:5000`
