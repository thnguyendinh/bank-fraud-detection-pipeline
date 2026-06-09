{{ config(materialized='table') }}

SELECT
    COUNT(TransactionID) AS total_transactions,
    SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) AS total_fraud_transactions,
    ROUND(
        SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(TransactionID), 0), 
        2
    ) AS fraud_rate_pct,
    SUM(TransactionAmount) AS total_transaction_amount,
    SUM(CASE WHEN IsFraud = 1 THEN TransactionAmount ELSE 0 END) AS total_fraudulent_amount,
    COUNT(DISTINCT UserID) AS unique_users,
    COUNT(DISTINCT MerchantID) AS unique_merchants,
    AVG(AnomalyScore) AS avg_anomaly_score,
    MAX(TransactionDate) AS last_transaction_date
FROM {{ ref('si_transactions_fact') }}