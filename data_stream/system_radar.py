import time
import psutil
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

class SystemAnomalyDetector:
    def __init__(self, warmup_samples=30):
        # contamination=0.05 means the AI expects roughly 5% of readings to be genuine spikes
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.warmup_samples = warmup_samples
        self.training_buffer = []
        self.is_trained = False

    def get_metrics(self):
        # Read live CPU utilization (%) and RAM utilization (%)
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return [cpu, ram]

    def run_radar(self):
        print("🚀 Booting Local Hardware Radar...")
        print(f"⏳ Phase 1: Calibrating AI... Gathering {self.warmup_samples} baseline samples.")

        # Prime the CPU reader (the very first call usually returns 0.0)
        psutil.cpu_percent()
        time.sleep(1)

        while True:
            metrics = self.get_metrics()
            timestamp = datetime.now().strftime("%H:%M:%S")

            # --- PHASE 1: WARM-UP ---
            if not self.is_trained:
                self.training_buffer.append(metrics)
                progress = len(self.training_buffer)
                
                # Dynamic terminal output (overwrites the same line)
                print(f"[{timestamp}] Calibrating: {progress}/{self.warmup_samples} | CPU: {metrics[0]:.1f}% | RAM: {metrics[1]:.1f}%", end="\r")

                if progress >= self.warmup_samples:
                    print("\n\n🧠 Baseline established. Training Isolation Forest...")
                    self.model.fit(self.training_buffer)
                    self.is_trained = True
                    print("🛡️ Phase 2: Active Monitoring Mode Engaged. (Press Ctrl+C to stop)\n")

            # --- PHASE 2: LIVE DETECTION ---
            else:
                # Scikit-learn expects a 2D array, so we wrap metrics in an extra set of brackets
                features = np.array([metrics])
                
                # Predict returns 1 for normal, -1 for anomaly
                prediction = self.model.predict(features)[0] 
                score = self.model.decision_function(features)[0]

                if prediction == -1:
                    print(f"🚨 ANOMALY DETECTED [{timestamp}] | CPU: {metrics[0]:.1f}% | RAM: {metrics[1]:.1f}% | AI Score: {score:.3f}")
                else:
                    # Silent monitoring: just overwrite the current line with a heartbeat
                    print(f"[{timestamp}] System Normal | CPU: {metrics[0]:.1f}% | RAM: {metrics[1]:.1f}%", end="\r")

            # Delay to avoid the radar itself using up too much CPU!
            time.sleep(1)

if __name__ == "__main__":
    detector = SystemAnomalyDetector(warmup_samples=30)
    try:
        detector.run_radar()
    except KeyboardInterrupt:
        print("\n\n🛑 Radar System Offline. Good work, Dev.")
