import streamlit as st
import pandas as pd
import numpy as np

# =========================
# SAFE PLOTLY IMPORT
# =========================
try:
    import plotly.express as px
    plotly_available = True
except:
    plotly_available = False

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="P5 Dynamic Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("📊 P5 Dynamic Dashboard")

st.markdown("---")

# =========================
# LOAD EXCEL FILE
# =========================
FILE_PATH = "P5 Dynamic Dashboard.xlsx"

@st.cache_data
def load_data():

    database = pd.read_excel(
        FILE_PATH,
        sheet_name="DATABASE"
    )

    dashboard = pd.read_excel(
        FILE_PATH,
        sheet_name="DASHBOARD"
    )

    lists = pd.read_excel(
        FILE_PATH,
        sheet_name="LISTS"
    )

    return database, dashboard, lists

DATABASE, DASHBOARD, LISTS = load_data()

# =========================
# CLEAN COLUMN NAMES
# =========================
DATABASE.columns = [
    str(col).strip()
    for col in DATABASE.columns
]

# =========================
# DATE COLUMN
# =========================
DATABASE["Del DATE"] = pd.to_datetime(
    DATABASE["Del DATE"],
    errors="coerce"
)

# =========================
# NUMERIC COLUMNS
# =========================
numeric_columns = [
    "UCS",
    "ORDER QTY",
    "DELIVER QTY",
    "OOS"
]

for col in numeric_columns:

    if col in DATABASE.columns:

        DATABASE[col] = pd.to_numeric(
            DATABASE[col],
            errors="coerce"
        ).fillna(0)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("FILTERS")

filtered_df = DATABASE.copy()

# OUTLET FILTER
if "OUTLET NAME" in DATABASE.columns:

    outlet_options = sorted(
        DATABASE["OUTLET NAME"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_outlet = st.sidebar.selectbox(
        "Select Outlet",
        ["ALL"] + outlet_options
    )

    if selected_outlet != "ALL":

        filtered_df = filtered_df[
            filtered_df["OUTLET NAME"]
            .astype(str)
            == selected_outlet
        ]

# YEAR FILTER
year_options = sorted(
    filtered_df["Del DATE"]
    .dropna()
    .dt.year
    .unique()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    year_options
)

filtered_df = filtered_df[
    filtered_df["Del DATE"].dt.year
    == selected_year
]

# MONTH FILTER
month_options = sorted(
    filtered_df["Del DATE"]
    .dropna()
    .dt.month
    .unique()
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    month_options
)

filtered_df = filtered_df[
    filtered_df["Del DATE"].dt.month
    == selected_month
]

# =========================
# KPI COMPUTATIONS
# =========================
act_ucs = (
    filtered_df["UCS"].sum()
    if "UCS" in filtered_df.columns
    else 0
)

order_qty = (
    filtered_df["ORDER QTY"].sum()
    if "ORDER QTY" in filtered_df.columns
    else 0
)

deliver_qty = (
    filtered_df["DELIVER QTY"].sum()
    if "DELIVER QTY" in filtered_df.columns
    else 0
)

oos_total = (
    filtered_df["OOS"].sum()
    if "OOS" in filtered_df.columns
    else 0
)

transactions = len(filtered_df)

# =========================
# KPI CARDS
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "ACT UCS",
        f"{act_ucs:,.0f}"
    )

with col2:
    st.metric(
        "ORDER QTY",
        f"{order_qty:,.0f}"
    )

with col3:
    st.metric(
        "DELIVER QTY",
        f"{deliver_qty:,.0f}"
    )

with col4:
    st.metric(
        "OOS",
        f"{oos_total:,.0f}"
    )

with col5:
    st.metric(
        "TRANSACTIONS",
        f"{transactions:,}"
    )

st.markdown("---")

# =========================
# DAILY UCS TREND
# =========================
if "UCS" in filtered_df.columns:

    st.subheader("Daily UCS Trend")

    daily_summary = (
        filtered_df
        .groupby("Del DATE", as_index=False)["UCS"]
        .sum()
        .sort_values("Del DATE")
    )

    if plotly_available:

        fig = px.line(
            daily_summary,
            x="Del DATE",
            y="UCS",
            markers=True,
            title="Daily UCS Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.line_chart(
            daily_summary.set_index("Del DATE")["UCS"]
        )

# =========================
# TOP PRODUCTS
# =========================
if "Description" in filtered_df.columns:

    st.subheader("Top 10 Products")

    product_summary = (
        filtered_df
        .groupby("Description", as_index=False)["UCS"]
        .sum()
        .sort_values("UCS", ascending=False)
        .head(10)
    )

    if plotly_available:

        fig2 = px.bar(
            product_summary,
            x="Description",
            y="UCS",
            title="Top 10 Products by UCS"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.bar_chart(
            product_summary.set_index("Description")["UCS"]
        )

# =========================
# OUTLET PERFORMANCE
# =========================
st.subheader("Outlet Performance")

group_columns = [
    col for col in [
        "OUTLET NUMBER",
        "OUTLET NAME"
    ]
    if col in filtered_df.columns
]

if len(group_columns) > 0:

    performance = (
        filtered_df
        .groupby(group_columns, as_index=False)
        .agg({
            "UCS": "sum",
            "ORDER QTY": "sum",
            "DELIVER QTY": "sum",
            "OOS": "sum"
        })
    )

    st.dataframe(
        performance,
        use_container_width=True,
        height=400
    )

# =========================
# DATABASE SHEET
# =========================
st.subheader("DATABASE SHEET")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)

# =========================
# DASHBOARD SHEET
# =========================
st.subheader("DASHBOARD SHEET")

st.dataframe(
    DASHBOARD,
    use_container_width=True,
    height=500
)

# =========================
# DOWNLOAD BUTTON
# =========================
csv = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Database",
    data=csv,
    file_name="filtered_database.csv",
    mime="text/csv"
)

# =========================
# FOOTER
# =========================
st.markdown("---")

st.caption(
    "Dynamic Dashboard Converted from Excel to Python Successfully"
)
