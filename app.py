# ============================================================
# COCA-COLA INSPIRED SALES DASHBOARD
# ROUTE CODE + OUTLET FILTER VERSION
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
# COCA-COLA THEME
# ============================================================

st.markdown("""
<style>

/* MAIN BACKGROUND */
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

/* TEXT */
h1, h2, h3, h4, h5 {
    color: white !important;
}

p, label, span {
    color: #ffeaea !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #4d0000,
        #7a0000
    );
}

/* KPI CARDS */
[data-testid="metric-container"] {

    background: rgba(255,255,255,0.10);

    border: 1px solid rgba(255,255,255,0.20);

    padding: 18px;

    border-radius: 20px;

    backdrop-filter: blur(10px);

}

/* CHARTS */
.stPlotlyChart {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 10px;

}

/* TABLE */
[data-testid="stDataFrame"] {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 10px;

}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<h1 style='text-align:center;'>
🥤 COCA-COLA SALES DASHBOARD
</h1>

<p style='text-align:center; color:white;'>
Premium Interactive Analytics Dashboard
</p>
""", unsafe_allow_html=True)

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

    # Convert columns to string
    df.columns = [
        str(col)
        for col in df.columns
    ]

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

    return df

# ============================================================
# LOAD DATAFRAME
# ============================================================

df = load_data(uploaded_file)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("⚙ FILTERS")

# ============================================================
# ROUTE CODE FILTER
# ============================================================

route_codes = []

if "ROUTE CODE" in df.columns:

    route_codes = sorted(
        df["ROUTE CODE"]
        .dropna()
        .astype(str)
        .unique()
    )

selected_routes = st.sidebar.multiselect(
    "Select Route Code",
    route_codes
)

# ============================================================
# OUTLET FILTER
# ============================================================

outlets = []

if "OUTLET NAME" in df.columns:

    outlets = sorted(
        df["OUTLET NAME"]
        .dropna()
        .astype(str)
        .unique()
    )

selected_outlets = st.sidebar.multiselect(
    "Select Outlet Name",
    outlets
)

# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()

# Route filter
if selected_routes:

    filtered_df = filtered_df[
        filtered_df["ROUTE CODE"]
        .astype(str)
        .isin(selected_routes)
    ]

# Outlet filter
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

TOTAL_OUTLETS = (
    filtered_df["OUTLET NAME"]
    .nunique()
)

# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 KPI SUMMARY")

c1, c2, c3, c4, c5 = st.columns(5)

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
    "UCS",
    f"{TOTAL_UCS:,.0f}"
)

c5.metric(
    "FILL RATE",
    f"{FILL_RATE:.2f}%"
)

st.markdown("---")

# ============================================================
# CHARTS
# ============================================================

chart1, chart2 = st.columns(2)

# ============================================================
# ROUTE PERFORMANCE
# ============================================================

with chart1:

    st.subheader("🚚 Route Performance")

    if "ROUTE CODE" in filtered_df.columns:

        route_summary = (
            filtered_df.groupby("ROUTE CODE")[
                ["ORDER QTY", "DELIVER QTY"]
            ]
            .sum()
            .reset_index()
        )

        fig_route = px.bar(
            route_summary,
            x="ROUTE CODE",
            y=["ORDER QTY", "DELIVER QTY"],
            barmode="group",
            template="plotly_dark"
        )

        fig_route.update_layout(

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(color="white"),

            height=450
        )

        st.plotly_chart(
            fig_route,
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
# DATABASE TABLE
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
