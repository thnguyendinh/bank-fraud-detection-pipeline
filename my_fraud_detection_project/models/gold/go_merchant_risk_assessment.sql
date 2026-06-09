{{ config(materialized='table') }}

SELECT
    MerchantID,
    COUNT(TransactionID) AS total_transactions,
    SUM(TransactionAmount) AS total_transaction_amount,
    AVG(TransactionAmount) AS avg_transaction_amount,
    SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) AS total_fraud_transactions,
    SUM(CASE WHEN IsFraud = 1 THEN TransactionAmount ELSE 0 END) AS total_fraudulent_amount,
    ROUND(
        SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(TransactionID), 0), 
        2
    ) AS merchant_fraud_rate_pct,
    AVG(AnomalyScore) AS avg_anomaly_score,
    CASE 
        WHEN AVG(AnomalyScore) >= 0.75 THEN 'HIGH_RISK'
        WHEN AVG(AnomalyScore) >= 0.50 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END AS merchant_risk_level
FROM {{ ref('si_transactions_fact') }}
GROUP BY MerchantID