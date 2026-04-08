import time
import random
import json
import uuid

def generate_transaction():
    """Generates a single simulated e-commerce transaction."""
    # Normal behavior: typical order volume, standard payment methods
    amount = round(random.uniform(10.0, 150.0), 2)
    payment_method = random.choice(["credit_card", "paypal", "debit_card"])
    is_fraud = False

    # Introduce a fraudulent anomaly ~5% of the time
    if random.random() < 0.05:
        amount = round(random.uniform(1000.0, 5000.0), 2)  # Suspiciously high order volume
        payment_method = random.choice(["crypto", "wire_transfer"]) # Unusual payment method
        is_fraud = True

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "amount": amount,
        "payment_method": payment_method,
        "user_id": random.randint(1000, 9999),
        "is_anomalous": is_fraud  # We keep this as ground truth to test our ML model later
    }
    return transaction

if __name__ == "__main__":
    print("🚀 Starting live transaction stream... Press Ctrl+C to stop.")
    try:
        while True:
            data = generate_transaction()
            # Print as a JSON string so other applications can easily parse it
            print(json.dumps(data))
            
            # Pause for a split second to simulate realistic, unpredictable live traffic
            time.sleep(random.uniform(0.1, 1.5))
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped.")
