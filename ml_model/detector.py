import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.warmup_size = 50
        self.training_buffer = []
        self.is_trained = False

    def process_transaction(self, transaction):
        # Convert categorical data to numbers for the model
        payment_map = {"credit_card": 1, "debit_card": 1, "paypal": 2, "crypto": 3, "wire_transfer": 3}
        features = np.array([[transaction['amount'], payment_map.get(transaction['payment_method'], 0)]])

        # PHASE 1: WARM-UP
        if not self.is_trained:
            self.training_buffer.append(features[0])
            current_count = len(self.training_buffer)
            
            if current_count >= self.warmup_size:
                self.model.fit(self.training_buffer)
                self.is_trained = True
                return {"status": "trained"}
            
            return {
                "status": "warming_up", 
                "current": current_count, 
                "total": self.warmup_size
            }

        # PHASE 2: LIVE DETECTION
        score = self.model.decision_function(features)[0]
        prediction = self.model.predict(features)[0]
        
        return {
            "status": "live",
            "transaction_id": transaction['id'],
            "amount": transaction['amount'],
            "payment_method": transaction['payment_method'],
            "anomaly_score": round(float(score), 4),
            "is_anomaly": bool(prediction == -1)
        }

    def update_model(self, amount, payment_method, is_actual_fraud):
        payment_map = {"credit_card": 1, "debit_card": 1, "paypal": 2, "crypto": 3, "wire_transfer": 3}
        payment_val = payment_map.get(payment_method, 0)
        self.training_buffer.append([amount, payment_val])
        if len(self.training_buffer) > 200: self.training_buffer.pop(0)
        self.model.fit(self.training_buffer)
