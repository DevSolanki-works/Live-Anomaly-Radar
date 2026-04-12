import pandas as pd
from sklearn.ensemble import IsolationForest
import warnings

# Suppress scikit-learn warnings for a clean terminal output
warnings.filterwarnings("ignore")

class AnomalyDetector:
    def __init__(self):
        # Initialize the Isolation Forest
        # contamination=0.05 tells the model we expect roughly 5% of data to be anomalous
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False
        self.training_buffer = []
        self.warmup_size = 50 # Number of transactions to observe before predicting

    def process_transaction(self, transaction):
        """Ingests a transaction, trains the model if warming up, or predicts if ready."""
        
        # 1. Feature Engineering: Convert text data to numbers for the math model
        # We'll map payment methods to risk tiers (1 = normal, 3 = high risk)
        payment_map = {"credit_card": 1, "debit_card": 1, "paypal": 2, "crypto": 3, "wire_transfer": 3}
        payment_val = payment_map.get(transaction['payment_method'], 0)
        
        # The features our model will analyze: [Amount, Payment_Method_Value]
        features = [[transaction['amount'], payment_val]]

        # 2. The Warm-Up Phase
        if not self.is_trained:
            self.training_buffer.append(features[0])
            print(f"🔄 Warming up model... ({len(self.training_buffer)}/{self.warmup_size})")
            
            if len(self.training_buffer) >= self.warmup_size:
                # Once we have enough data, fit the model to establish "normal"
                self.model.fit(self.training_buffer)
                self.is_trained = True
                print("✅ Model trained and ready for live detection!\n" + "="*50)
            return None # Don't return predictions during warm-up

        # 3. The Live Prediction Phase
        # predict() returns 1 for normal data, -1 for anomalies
        prediction = self.model.predict(features)[0]
        
        # decision_function() gives us a confidence score (negative means highly abnormal)
        score = self.model.decision_function(features)[0]

        is_anomaly = True if prediction == -1 else False
        
        return {
            "transaction_id": transaction["transaction_id"],
            "amount": transaction["amount"],
            "payment_method": transaction["payment_method"],
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 3),
            "ground_truth_fraud": transaction["is_anomalous"] # Keeping this to check our accuracy!
        }
    
    def update_model(self, amount, payment_method, is_actual_fraud):
        """Human-in-the-loop feedback to retrain the model."""
        print(f"🧠 FEEDBACK RECEIVED: Amount: ${amount}, Fraud: {is_actual_fraud}. Retraining...")
        
        payment_map = {"credit_card": 1, "debit_card": 1, "paypal": 2, "crypto": 3, "wire_transfer": 3}
        payment_val = payment_map.get(payment_method, 0)
        
        # Add the corrected data point to our memory buffer
        # In a real system, we'd handle fraud labels differently, but for an 
        # unsupervised Isolation Forest, we just feed it more data to understand the "landscape"
        self.training_buffer.append([amount, payment_val])
        
        # Keep buffer from getting infinitely large (keep the newest 200)
        if len(self.training_buffer) > 200:
            self.training_buffer.pop(0)
            
        # Retrain the model instantly
        self.model.fit(self.training_buffer)
        print("✅ Model retrained successfully with new human feedback!")

if __name__ == "__main__":
    # --- LOCAL TESTING BLOCK ---
    import sys
    import os
    import time
    
    # Add the parent directory to the path so we can import our generator
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_stream.generator import generate_transaction

    print("🧠 Booting up ML Engine...")
    detector = AnomalyDetector()

    try:
        while True:
            # Get a live transaction from Phase 1
            tx = generate_transaction()
            
            # Feed it to the brain
            result = detector.process_transaction(tx)
            
            if result:
                if result["is_anomaly"]:
                    print(f"🚨 ANOMALY CAUGHT! Score: {result['anomaly_score']:>6} | Amount: ${result['amount']:>7.2f} | Was actually fraud? {result['ground_truth_fraud']}")
                else:
                    print(f"✅ Normal tx cleared. Amount: ${result['amount']:>7.2f}")
            
            time.sleep(0.1) # Run it fast for testing
    except KeyboardInterrupt:
        print("\n🛑 Engine shut down.")

