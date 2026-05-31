# FINAL ADJUSTED DASHBOARD CODE

This version is fully adjusted to your uploaded Excel structure:

`P5 Dynamic Dashboard 053026.xlsm`

It now uses the `DATABASE` sheet correctly.

Features:

* KPI Summary
* Route Analysis
* Top Outlet Ranking
* SKU Analysis
* OOS Monitoring
* Interactive Filters
* Date Filtering
* Route Filtering
* Outlet Filtering
* Dynamic Charts
* Streamlit Cloud Ready
* Duplicate Column Protection
* Professional UI

---

```python
# ============================================================
# BD BATANGAS ADVANCED SALES DASHBOARD
# FULLY ADJUSTED TO DATABASE SHEET
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BD Batangas Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #0f172a, #111827);
}

h1,h2,h3,h4 {
    color: white !important;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.title("📊 BD BATANGAS SALES DASHBOARD")
st.caption("Advanced Dynamic Analytics Dashboard")

# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsm", "xlsx"]
)

if uploaded_file is None:
    st.info("Please upload your Excel file.")
    st.stop()

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data

def load_data(file):

    df = pd.read_excel(
        file,
        sheet_name="DATABASE"
    )

    # ========================================================
    # REMOVE EMPTY COLUMNS
    # ========================================================

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # ========================================================
    # REMOVE EMPTY ROWS
    # ========================================================

    df = df.dropna(
        subset=["OUTLET NAME"],
        how="all"
    )

    # ========================================================
    # CONVERT NUMERIC COLUMNS
    # ========================================================

    numeric_cols = [
        "ORDER QTY",
        "DELIVER QTY",
        "OOS",
        "UCS"
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    # ========================================================
    # DATE CONVERSION
    # ========================================================

    if "Del DATE" in df.columns:

        df["Del DATE"] = pd.to_datetime(
            df["Del DATE"],
            errors="coerce"
        )

    return df

# ============================================================
# LOAD DATAFRAME
# ============================================================

df = load_data(uploaded_file)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("⚙ FILTERS")

# ROUTE FILTER
routes = sorted(
    df["Shipment"]
    .dropna()
    .astype(str)
    .unique()
)

selected_routes = st.sidebar.multiselect(
    "Select Shipment",
    routes
)

# OUTLET FILTER
outlets = sorted(
    df["OUTLET NAME"]
    .dropna()
    .astype(str)
    .unique()
)

selected_outlets = st.sidebar.multiselect(
    "Select Outlet",
    outlets
)

# DATE FILTER
if "Del DATE" in df.columns:

    min_date = df["Del DATE"].min()
    max_date = df["Del DATE"].max()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()

if selected_routes:

    filtered_df = filtered_df[
        filtered_df["Shipment"]
        .astype(str)
        .isin(selected_routes)
    ]

if selected_outlets:

    filtered_df = filtered_df[
        filtered_df["OUTLET NAME"]
        .astype(str)
        .isin(selected_outlets)
    ]

if len(selected_dates) == 2:

    start_date = pd.to_datetime(selected_dates[0])
    end_date = pd.to_datetime(selected_dates[1])

    filtered_df = filtered_df[
        (filtered_df["Del DATE"] >= start_date) &
        (filtered_df["Del DATE"] <= end_date)
    ]

# ============================================================
# KPI CALCULATIONS
# ============================================================

TOTAL_ORDER = filtered_df["ORDER QTY"].sum()
TOTAL_DELIVERED = filtered_df["DELIVER QTY"].sum()
TOTAL_OOS = filtered_df["OOS"].sum()
TOTAL_UCS = filtered_df["UCS"].sum()

TOTAL_OUTLETS = filtered_df["OUTLET NAME"].nunique()
TOTAL_SKU = filtered_df["Description"].nunique()

FILL_RATE = (
    (TOTAL_DELIVERED / TOTAL_ORDER) * 100
    if TOTAL_ORDER != 0 else 0
)

# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 KPI SUMMARY")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("ORDER QTY", f"{TOTAL_ORDER:,.0f}")
c2.metric("DELIVERED", f"{TOTAL_DELIVERED:,.0f}")
c3.metric("OOS", f"{TOTAL_OOS:,.0f}")
c4.metric("UCS", f"{TOTAL_UCS:,.0f}")
c5.metric("OUTLETS", f"{TOTAL_OUTLETS}")
c6.metric("FILL RATE", f"{FILL_RATE:.2f}%")

st.markdown("---")

# ============================================================
# CHARTS ROW 1
# ============================================================

chart1, chart2 = st.columns(2)

# ============================================================
# SHIPMENT PERFORMANCE
# ============================================================

with chart1:

    st.subheader("🚚 Shipment Performance")

    shipment_summary = (
        filtered_df.groupby("Shipment")[[
            "ORDER QTY",
            "DELIVER QTY"
        ]]
        .sum()
        .reset_index()
    )

    fig_ship = px.bar(
        shipment_summary,
        x="Shipment",
        y=["ORDER QTY", "DELIVER QTY"],
        barmode="group",
        template="plotly_dark"
    )

    fig_ship.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(
        fig_ship,
        use_container_width=True
    )

# ============================================================
# TOP OUTLETS
# ============================================================

with chart2:

    st.subheader("🏆 Top Outlets")

    top_outlets = (
        filtered_df.groupby("OUTLET NAME")["UCS"]
        .sum()
        .reset_index()
        .sort_values(
            by="UCS",
            ascending=False
        )
        .head(10)
    )

    fig_outlet = px.bar(
        top_outlets,
        x="UCS",
        y="OUTLET NAME",
        orientation="h",
        template="plotly_dark"
    )

    fig_outlet.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(
        fig_outlet,
        use_container_width=True
    )

# ============================================================
# CHARTS ROW 2
# ============================================================

chart3, chart4 = st.columns(2)

# ============================================================
# TOP SKU
# ============================================================

with chart3:

    st.subheader("🥤 Top SKU by UCS")

    top_sku = (
        filtered_df.groupby("Description")["UCS"]
        .sum()
        .reset_index()
        .sort_values(
            by="UCS",
            ascending=False
        )
        .head(10)
    )

    fig_sku = px.bar(
        top_sku,
        x="UCS",
        y="Description",
        orientation="h",
        template="plotly_dark"
    )

    fig_sku.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(
        fig_sku,
        use_container_width=True
    )

# ============================================================
# OOS DISTRIBUTION
# ============================================================

with chart4:

    st.subheader("📦 OOS Distribution")

    pie_df = pd.DataFrame({
        "Category": [
            "Delivered",
            "OOS"
        ],
        "Value": [
            TOTAL_DELIVERED,
            TOTAL_OOS
        ]
    })

    fig_pie = px.pie(
        pie_df,
        names="Category",
        values="Value",
        hole=0.5,
        template="plotly_dark"
    )

    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📋 Transaction Database")

safe_df = filtered_df.copy()

safe_df.columns = [
    str(col)
    for col in safe_df.columns
]

safe_df = safe_df.loc[
    :,
    ~safe_df.columns.duplicated()
]

st.dataframe(
    safe_df,
    use_container_width=True,
    height=500
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption("Advanced Dashboard • Streamlit + Plotly")

```

---

# REQUIREMENTS.TXT

```txt
streamlit
```
