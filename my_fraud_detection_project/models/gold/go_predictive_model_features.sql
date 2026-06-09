{{ config(materialized='table') }}

SELECT
    t.TransactionID,
    t.UserID,
    t.TransactionAmount,
    t.AnomalyScore,
    t.SuspiciousFlag,
    t.PaymentMethod,
    t.DeviceType,
    t.TransactionType,
    t.IsFraud,
    u.Age,
    u.AccountStatus,
    u.UserProfileCompleteness,
    u.PreviousFraudAttempts,
    CASE 
        WHEN t.TransactionAmount >= 3000000 THEN 1 
        ELSE 0 
    END AS is_high_amount_transaction,
    CASE 
        WHEN u.PreviousFraudAttempts > 0 THEN 1 
        ELSE 0 
    END AS has_previous_fraud_attempts
FROM {{ ref('si_transactions_fact') }} t
LEFT JOIN {{ ref('si_users_dimension') }} u
    ON t.UserID = u.UserID