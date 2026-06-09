import os
import random
import uuid
from datetime import datetime, timedelta

import pandas as pd


def random_date(year: int) -> datetime:
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_transactions(year: int, n_rows: int = 10000) -> pd.DataFrame:
    users = [f"U{str(i).zfill(6)}" for i in range(1, 2001)]
    merchants = [f"M{str(i).zfill(5)}" for i in range(1, 501)]
    devices = [f"D{str(i).zfill(6)}" for i in range(1, 3001)]

    transaction_types = ["purchase", "transfer", "cash_withdrawal", "bill_payment", "online_payment"]
    payment_methods = ["debit_card", "credit_card", "bank_transfer", "mobile_wallet"]
    device_types = ["mobile", "desktop", "atm", "pos"]
    locations = ["Ho Chi Minh City", "Hanoi", "Da Nang", "Singapore", "Bangkok", "Kuala Lumpur"]
    statuses = ["success", "failed", "pending"]
    genders = ["M", "F"]
    currencies = ["VND", "USD"]

    rows = []

    for _ in range(n_rows):
        user_id = random.choice(users)
        tx_date = random_date(year)
        amount = round(random.expovariate(1 / 700000), 2)

        # Một số điều kiện tăng rủi ro fraud
        high_amount = amount > 3000000
        risky_location = random.random() < 0.08
        previous_fraud_attempts = random.choices([0, 1, 2, 3], weights=[85, 10, 4, 1])[0]
        suspicious_flag = 1 if high_amount or risky_location or previous_fraud_attempts > 1 else 0

        base_score = random.uniform(0.01, 0.45)
        if high_amount:
            base_score += random.uniform(0.15, 0.25)
        if risky_location:
            base_score += random.uniform(0.15, 0.25)
        if previous_fraud_attempts > 0:
            base_score += random.uniform(0.05, 0.2)

        anomaly_score = min(round(base_score, 4), 0.99)
        is_fraud = 1 if anomaly_score >= 0.72 or (suspicious_flag == 1 and random.random() < 0.25) else 0

        row = {
            "TransactionID": str(uuid.uuid4()),
            "UserID": user_id,
            "TransactionDate": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            "TransactionTime": tx_date.strftime("%H:%M:%S"),
            "TransactionAmount": amount,
            "TransactionType": random.choice(transaction_types),
            "MerchantID": random.choice(merchants),
            "Currency": random.choice(currencies),
            "TransactionStatus": random.choices(statuses, weights=[92, 5, 3])[0],
            "DeviceType": random.choice(device_types),
            "DeviceID": random.choice(devices),
            "IP_Address": f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}",
            "PaymentMethod": random.choice(payment_methods),
            "Location": random.choice(locations),
            "LocationCoordinates": f"{round(random.uniform(8.0, 22.0), 6)},{round(random.uniform(102.0, 109.0), 6)}",
            "Age": random.randint(18, 70),
            "Gender": random.choice(genders),
            "AccountCreationDate": (tx_date - timedelta(days=random.randint(30, 3000))).strftime("%Y-%m-%d"),
            "AccountStatus": random.choices(["active", "blocked", "under_review"], weights=[94, 2, 4])[0],
            "UserProfileCompleteness": round(random.uniform(0.45, 1.0), 2),
            "PreviousFraudAttempts": previous_fraud_attempts,
            "SuspiciousFlag": suspicious_flag,
            "IsFraud": is_fraud,
            "ReviewStatus": "pending_review" if is_fraud else "auto_approved",
            "AnomalyScore": anomaly_score,
            "year": year,
        }

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)

    for year in [2022, 2023, 2024,2025,2026]:
        df = generate_transactions(year, n_rows=10000)
        year_dir = os.path.join(output_dir, f"year={year}")
        os.makedirs(year_dir, exist_ok=True)

        output_path = os.path.join(year_dir, f"transactions_{year}.csv")
        df.to_csv(output_path, index=False)
        print(f"Created {output_path}: {len(df)} rows")


if __name__ == "__main__":
    main()