{{ config(
    materialized='incremental',
    unique_key='DeviceID'
) }}

WITH ranked_devices AS (
    SELECT
        DeviceID,
        DeviceType,
        IP_Address,
        ROW_NUMBER() OVER (
            PARTITION BY DeviceID
            ORDER BY TransactionDate DESC
        ) AS rn
    FROM {{ ref('br_fraud_detection_raw_data_historical') }}
    WHERE DeviceID IS NOT NULL
)

SELECT
    DeviceID,
    DeviceType,
    IP_Address
FROM ranked_devices
WHERE rn = 1