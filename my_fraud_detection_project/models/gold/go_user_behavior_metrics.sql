{{ config(materialized='table') }}

SELECT
    UserID,
    COUNT(TransactionID) AS total_transactions,
    AVG(TransactionAmount) AS avg_transaction_amount,
    MAX(TransactionAmount) AS max_transaction_amount,
    SUM(TransactionAmount) AS total_transaction_amount,
    SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) AS total_fraud_transactions,
    ROUND(
        SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(TransactionID), 0), 
        2
    ) AS user_fraud_rate_pct,
    COUNT(DISTINCT DeviceID) AS unique_devices,
    COUNT(DISTINCT MerchantID) AS unique_merchants,
    MAX(TransactionDate) AS last_transaction_date,
    MIN(TransactionDate) AS first_transaction_date
FROM {{ ref('si_transactions_fact') }}
GROUP BY UserID