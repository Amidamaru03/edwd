# ============================================================
# COCA-COLA INSPIRED SALES DASHBOARD
# PREMIUM RED EDITION
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Coca-Cola Sales Dashboard",
    page_icon="🥤",
    layout="wide"
)

# ============================================================
# COCA-COLA THEME CSS
# ============================================================

st.markdown("""
<style>

/* =========================================================
MAIN BACKGROUND
========================================================= */

.stApp {
    background:
    linear-gradient(
        135deg,
        #3b0000 0%,
        #7a0000 35%,
        #b30000 70%,
        #ff0000 100%
    );
}

/* =========================================================
TEXT COLORS
========================================================= */

h1, h2, h3, h4, h5 {
    color: white !important;
}

p, label, span {
    color: #ffeaea !important;
}

/* =========================================================
SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #4d0000,
        #7a0000
    );
    border-right: 2px solid rgba(255,255,255,0.15);
}

/* =========================================================
KPI CARDS
========================================================= */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.10);

    border: 1px solid rgba(255,255,255,0.20);

    padding: 18px;

    border-radius: 22px;

    backdrop-filter: blur(12px);

    box-shadow:
        0 8px 32px rgba(0,0,0,0.25);

}

/* =========================================================
CHART CONTAINER
========================================================= */

.stPlotlyChart {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 10px;

    border: 1px solid rgba(255,255,255,0.12);

    backdrop-filter: blur(10px);

}

/* =========================================================
DATAFRAME
========================================================= */

[data-testid="stDataFrame"] {

    background: rgba(255,255,255,0.06);

    border-radius: 20px;

    padding: 10px;

}

/* =========================================================
BUTTONS
========================================================= */

.stButton>button {

    background: #ff1a1a;

    color: white;

    border-radius: 12px;

    border: none;

    font-weight: bold;

}

.stButton>button:hover {

    background: #cc0000;

    color: white;

}

/* =========================================================
UPLOAD AREA
========================================================= */

[data-testid="stFileUploader"] {

    background: rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 15px;

}

/* =========================================================
HEADER
========================================================= */

.dashboard-title {

    font-size: 48px;

    font-weight: 800;

    color: white;

    text-align: center;

    margin-bottom: 5px;

}

.dashboard-subtitle {

    text-align: center;

    color: #ffe5e5;

    font-size: 16px;

    margin-bottom: 20px;

}

/* =========================================================
DIVIDER
========================================================= */

hr {

    border: 1px solid rgba(255,255,255,0.12);

}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="dashboard-title">
🥤 COCA-COLA SALES DASHBOARD
</div>

<div class="dashboard-subtitle">
Premium Interactive Analytics Dashboard
</div>
""", unsafe_allow_html=True)

# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsm", "xlsx"]
)

if uploaded_file is None:

    st.info("Upload your Coca-Cola sales Excel file.")

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

    # Remove unnamed columns
    df = df.loc[
        :,
        ~df.columns.astype(str).str.contains("^Unnamed")
    ]

    # Remove duplicate columns
    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    # Convert headers to string
    df.columns = [
        str(col)
        for col in df.columns
    ]

    # Remove empty rows
    if "OUTLET NAME" in df.columns:

        df = df.dropna(
            subset=["OUTLET NAME"]
        )

    # Numeric conversion
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

    # Date conversion
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

st.sidebar.title("⚙ FILTERS")

# Shipment filter
shipments = []

if "Shipment" in df.columns:

    shipments = sorted(
        df["Shipment"]
        .dropna()
        .astype(str)
        .unique()
    )

selected_shipments = st.sidebar.multiselect(
    "Select Shipment",
    shipments
)

# Outlet filter
outlets = []

if "OUTLET NAME" in df.columns:

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

# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()

if selected_shipments:

    filtered_df = filtered_df[
        filtered_df["Shipment"]
        .astype(str)
        .isin(selected_shipments)
    ]

if selected_outlets:

    filtered_df = filtered_df[
        filtered_df["OUTLET NAME"]
        .astype(str)
        .isin(selected_outlets)
    ]

# ============================================================
# KPI CALCULATIONS
# ============================================================

TOTAL_ORDER = filtered_df["ORDER QTY"].sum()
TOTAL_DELIVERED = filtered_df["DELIVER QTY"].sum()
TOTAL_OOS = filtered_df["OOS"].sum()
TOTAL_UCS = filtered_df["UCS"].sum()

FILL_RATE = (
    (TOTAL_DELIVERED / TOTAL_ORDER) * 100
    if TOTAL_ORDER != 0 else 0
)

# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 KPI SUMMARY")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "ORDER QTY",
    f"{TOTAL_ORDER:,.0f}"
)

c2.metric(
    "DELIVERED",
    f"{TOTAL_DELIVERED:,.0f}"
)

c3.metric(
    "OOS",
    f"{TOTAL_OOS:,.0f}"
)

c4.metric(
    "FILL RATE",
    f"{FILL_RATE:.2f}%"
)

st.markdown("---")

# ============================================================
# CHARTS
# ============================================================

chart1, chart2 = st.columns(2)

# ============================================================
# SHIPMENT PERFORMANCE
# ============================================================

with chart1:

    st.subheader("🚚 Shipment Performance")

    shipment_summary = (
        filtered_df.groupby("Shipment")[
            ["ORDER QTY", "DELIVER QTY"]
        ]
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

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(color="white"),

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

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(color="white"),

        height=450
    )

    st.plotly_chart(
        fig_outlet,
        use_container_width=True
    )

# ============================================================
# PIE CHART
# ============================================================

st.subheader("🥤 Delivery Distribution")

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
    hole=0.6,
    template="plotly_dark"
)

fig_pie.update_layout(

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    font=dict(color="white"),

    height=500
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

# ============================================================
# TABLE
# ============================================================

st.subheader("📋 Sales Database")

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

st.markdown("""
<center>
<p style='color:white;'>
🥤 Coca-Cola Inspired Dashboard • Powered by Streamlit
</p>
</center>
""", unsafe_allow_html=True)
