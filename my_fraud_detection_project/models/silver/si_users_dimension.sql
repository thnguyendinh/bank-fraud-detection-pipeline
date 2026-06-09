{{ config(
    materialized='incremental',
    unique_key='UserID'
) }}

WITH ranked_users AS (
    SELECT
        UserID,
        Age,
        Gender,
        AccountCreationDate,
        AccountStatus,
        UserProfileCompleteness,
        PreviousFraudAttempts,
        Location AS UserLocation,
        ROW_NUMBER() OVER (
            PARTITION BY UserID 
            ORDER BY TransactionDate DESC
        ) AS rn
    FROM {{ ref('br_fraud_detection_raw_data_historical') }}
)

SELECT
    UserID,
    Age,
    Gender,
    AccountCreationDate,
    AccountStatus,
    UserProfileCompleteness,
    PreviousFraudAttempts,
    UserLocation
FROM ranked_users
WHERE rn = 1