{{ config(
    materialized='incremental',
    unique_key='TransactionID'
) }}

WITH source_data AS (
    SELECT *
    FROM {{ ref('br_fraud_detection_raw_data_historical') }}

    {% if is_incremental() %}
        WHERE TransactionDate > (
            SELECT COALESCE(MAX(TransactionDate), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
)

SELECT DISTINCT
    TransactionID,
    UserID,
    TransactionDate,
    TransactionTime,
    TransactionAmount,
    TransactionType,
    MerchantID,
    Currency,
    TransactionStatus,
    DeviceType,
    DeviceID,
    IP_Address,
    PaymentMethod,
    Location,
    LocationCoordinates,
    SuspiciousFlag,
    IsFraud,
    ReviewStatus,
    AnomalyScore,
    year
FROM source_data