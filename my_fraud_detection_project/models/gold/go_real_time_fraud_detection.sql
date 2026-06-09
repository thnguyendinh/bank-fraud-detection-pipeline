{{ config(materialized='view') }}

SELECT
    TransactionID,
    UserID,
    TransactionDate,
    TransactionAmount,
    TransactionType,
    MerchantID,
    PaymentMethod,
    DeviceID,
    DeviceType,
    Location,
    SuspiciousFlag,
    IsFraud,
    AnomalyScore,
    CASE
        WHEN AnomalyScore >= 0.85 THEN 'CRITICAL'
        WHEN AnomalyScore >= 0.70 THEN 'HIGH'
        WHEN AnomalyScore >= 0.50 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_level,
    CASE
        WHEN AnomalyScore >= 0.70 OR SuspiciousFlag = 1 THEN 1
        ELSE 0
    END AS requires_manual_review
FROM {{ ref('si_transactions_fact') }}
WHERE AnomalyScore >= 0.50 
   OR SuspiciousFlag = 1 
   OR IsFraud = 1