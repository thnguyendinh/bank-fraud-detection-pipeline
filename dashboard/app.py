import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector


st.set_page_config(
    page_title="Bank Fraud Detection Dashboard",
    page_icon="🏦",
    layout="wide"
)


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        role=st.secrets["snowflake"]["role"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
    )


@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        return cur.fetch_pandas_all()
    finally:
        cur.close()


st.title("🏦 Bank Fraud Detection Analytics Dashboard")
st.caption("End-to-end DE project: AWS S3 → Snowflake → dbt → Streamlit")

# =========================
# LOAD DATA
# =========================

kpi_df = run_query("""
    SELECT *
    FROM GO_FRAUD_DETECTION_DASHBOARD_METRICS
""")

transactions_df = run_query("""
    SELECT *
    FROM SI_TRANSACTIONS_FACT
    LIMIT 50000
""")

risky_users_df = run_query("""
    SELECT *
    FROM GO_USER_BEHAVIOR_METRICS
    ORDER BY USER_FRAUD_RATE_PCT DESC, TOTAL_FRAUD_TRANSACTIONS DESC
    LIMIT 50
""")

risky_merchants_df = run_query("""
    SELECT *
    FROM GO_MERCHANT_RISK_ASSESSMENT
    ORDER BY MERCHANT_FRAUD_RATE_PCT DESC, TOTAL_FRAUD_TRANSACTIONS DESC
    LIMIT 50
""")

high_risk_tx_df = run_query("""
    SELECT *
    FROM GO_REAL_TIME_FRAUD_DETECTION
    ORDER BY ANOMALYSCORE DESC
    LIMIT 200
""")


# =========================
# KPI SECTION
# =========================

st.header("1. Fraud Overview")

if not kpi_df.empty:
    kpi = kpi_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Transactions", f"{int(kpi['TOTAL_TRANSACTIONS']):,}")
    col2.metric("Fraud Transactions", f"{int(kpi['TOTAL_FRAUD_TRANSACTIONS']):,}")
    col3.metric("Fraud Rate", f"{float(kpi['FRAUD_RATE_PCT']):.2f}%")
    col4.metric("Avg Anomaly Score", f"{float(kpi['AVG_ANOMALY_SCORE']):.3f}")

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Total Amount", f"{float(kpi['TOTAL_TRANSACTION_AMOUNT']):,.0f}")
    col6.metric("Fraud Amount", f"{float(kpi['TOTAL_FRAUDULENT_AMOUNT']):,.0f}")
    col7.metric("Unique Users", f"{int(kpi['UNIQUE_USERS']):,}")
    col8.metric("Unique Merchants", f"{int(kpi['UNIQUE_MERCHANTS']):,}")


# =========================
# FILTERS
# =========================

st.sidebar.header("Filters")

if "PAYMENTMETHOD" in transactions_df.columns:
    payment_methods = sorted(transactions_df["PAYMENTMETHOD"].dropna().unique().tolist())
    selected_payment = st.sidebar.multiselect(
        "Payment Method",
        payment_methods,
        default=payment_methods
    )
else:
    selected_payment = []

if "TRANSACTIONTYPE" in transactions_df.columns:
    transaction_types = sorted(transactions_df["TRANSACTIONTYPE"].dropna().unique().tolist())
    selected_type = st.sidebar.multiselect(
        "Transaction Type",
        transaction_types,
        default=transaction_types
    )
else:
    selected_type = []

filtered_df = transactions_df.copy()

if selected_payment and "PAYMENTMETHOD" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["PAYMENTMETHOD"].isin(selected_payment)]

if selected_type and "TRANSACTIONTYPE" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["TRANSACTIONTYPE"].isin(selected_type)]


# =========================
# CHARTS
# =========================

st.header("2. Fraud Analysis")

col1, col2 = st.columns(2)

with col1:
    if "PAYMENTMETHOD" in filtered_df.columns and "ISFRAUD" in filtered_df.columns:
        fraud_by_payment = (
            filtered_df.groupby("PAYMENTMETHOD")["ISFRAUD"]
            .sum()
            .reset_index()
            .rename(columns={"ISFRAUD": "FRAUD_COUNT"})
        )

        fig = px.bar(
            fraud_by_payment,
            x="PAYMENTMETHOD",
            y="FRAUD_COUNT",
            title="Fraud Count by Payment Method"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "TRANSACTIONTYPE" in filtered_df.columns and "ISFRAUD" in filtered_df.columns:
        fraud_by_type = (
            filtered_df.groupby("TRANSACTIONTYPE")["ISFRAUD"]
            .sum()
            .reset_index()
            .rename(columns={"ISFRAUD": "FRAUD_COUNT"})
        )

        fig = px.bar(
            fraud_by_type,
            x="TRANSACTIONTYPE",
            y="FRAUD_COUNT",
            title="Fraud Count by Transaction Type"
        )
        st.plotly_chart(fig, use_container_width=True)


col3, col4 = st.columns(2)

with col3:
    if "LOCATION" in filtered_df.columns and "ISFRAUD" in filtered_df.columns:
        fraud_by_location = (
            filtered_df.groupby("LOCATION")["ISFRAUD"]
            .sum()
            .reset_index()
            .rename(columns={"ISFRAUD": "FRAUD_COUNT"})
            .sort_values("FRAUD_COUNT", ascending=False)
        )

        fig = px.bar(
            fraud_by_location,
            x="LOCATION",
            y="FRAUD_COUNT",
            title="Fraud Count by Location"
        )
        st.plotly_chart(fig, use_container_width=True)

with col4:
    if "ANOMALYSCORE" in filtered_df.columns:
        fig = px.histogram(
            filtered_df,
            x="ANOMALYSCORE",
            nbins=30,
            title="Anomaly Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)


# =========================
# RISK TABLES
# =========================

st.header("3. High-Risk Users")

st.dataframe(
    risky_users_df,
    use_container_width=True,
    hide_index=True
)

st.header("4. Merchant Risk Assessment")

st.dataframe(
    risky_merchants_df,
    use_container_width=True,
    hide_index=True
)

st.header("5. High-Risk Transaction Monitoring")

st.dataframe(
    high_risk_tx_df,
    use_container_width=True,
    hide_index=True
)


# =========================
# RAW DATA SAMPLE
# =========================

with st.expander("View Transaction Fact Sample"):
    st.dataframe(
        filtered_df.head(1000),
        use_container_width=True,
        hide_index=True
    )