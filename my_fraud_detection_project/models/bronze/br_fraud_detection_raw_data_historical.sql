{{ config(
    materialized='incremental',
    unique_key='TransactionID'
) }}

WITH raw_data AS (
    SELECT
        TransactionID::string AS TransactionID,
        UserID::string AS UserID,
        TransactionDate::timestamp AS TransactionDate,
        TransactionTime::string AS TransactionTime,
        TransactionAmount::float AS TransactionAmount,
        TransactionType::string AS TransactionType,
        MerchantID::string AS MerchantID,
        Currency::string AS Currency,
        TransactionStatus::string AS TransactionStatus,
        DeviceType::string AS DeviceType,
        DeviceID::string AS DeviceID,
        IP_Address::string AS IP_Address,
        PaymentMethod::string AS PaymentMethod,
        Location::string AS Location,
        LocationCoordinates::string AS LocationCoordinates,
        Age::int AS Age,
        Gender::string AS Gender,
        AccountCreationDate::date AS AccountCreationDate,
        AccountStatus::string AS AccountStatus,
        UserProfileCompleteness::float AS UserProfileCompleteness,
        PreviousFraudAttempts::int AS PreviousFraudAttempts,
        SuspiciousFlag::int AS SuspiciousFlag,
        IsFraud::int AS IsFraud,
        ReviewStatus::string AS ReviewStatus,
        AnomalyScore::float AS AnomalyScore,
        year::int AS year,
        CURRENT_TIMESTAMP() AS loaded_at
    FROM {{ source('fraud_detection', 'transactions_staging') }}

    {% if is_incremental() %}
        WHERE TransactionDate > (
            SELECT COALESCE(MAX(TransactionDate), '1900-01-01') 
            FROM {{ this }}
        )
    {% endif %}
)

SELECT DISTINCT *
FROM raw_data
WHERE TransactionID IS NOT NULL
  AND UserID IS NOT NULL
  AND TransactionAmount IS NOT NULL