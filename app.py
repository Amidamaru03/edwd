# ============================================================
# BD BATANGAS SALES DASHBOARD
# FINAL CLEAN ADVANCED VERSION
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #0f172a, #111827);
}

h1, h2, h3, h4 {
    color: white !important;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.metric-container {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

.small-text {
    color: #d1d5db;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<h1>📊 BD BATANGAS SALES DASHBOARD</h1>
<p class='small-text'>
Advanced Interactive Analytics Dashboard
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xlsm"]
)

if uploaded_file is None:
    st.info("Please upload your Excel sales file.")
    st.stop()

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(file):

    raw = pd.read_excel(
        file,
        sheet_name="OUTLETS"
    )

    # ========================================================
    # GET HEADERS
    # ========================================================

    headers = raw.iloc[1].astype(str)

    unique_headers = []
    counter = {}

    for col in headers:

        if col in counter:

            counter[col] += 1

            unique_headers.append(
                f"{col}_{counter[col]}"
            )

        else:

            counter[col] = 0

            unique_headers.append(col)

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = raw.iloc[2:].copy()

    df.columns = unique_headers

    # ========================================================
    # REMOVE EMPTY ROWS
    # ========================================================

    if "Customer Name" in df.columns:

        df = df.dropna(
            subset=["Customer Name"]
        )

    # ========================================================
    # RESET INDEX
    # ========================================================

    df.reset_index(
        drop=True,
        inplace=True
    )

    # ========================================================
    # RENAME COLUMNS
    # ========================================================

    rename_map = {}

    for col in df.columns:

        col_str = str(col)

        if "Customer Name" in col_str:
            rename_map[col] = "Customer_Name"

        elif "Customer No" in col_str:
            rename_map[col] = "Customer_No"

        elif "ACTUAL_UCS" in col_str:
            rename_map[col] = "Actual_UCS"

        elif "LY_UCS" in col_str:
            rename_map[col] = "LY_UCS"

        elif "S&OP_UCS" in col_str:
            rename_map[col] = "SOP_UCS"

        elif "ROUTE" in col_str:
            rename_map[col] = "ROUTE"

    df.rename(
        columns=rename_map,
        inplace=True
    )

    # ========================================================
    # REMOVE DUPLICATE COLUMNS
    # ========================================================

    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    numeric_cols = [
        "Actual_UCS",
        "LY_UCS",
        "SOP_UCS"
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

st.sidebar.title("⚙ Dashboard Filters")

routes = []

if "ROUTE" in df.columns:

    routes = sorted(
        df["ROUTE"]
        .dropna()
        .astype(str)
        .unique()
    )

selected_routes = st.sidebar.multiselect(
    "Select Route",
    routes
)

# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()

if selected_routes and "ROUTE" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["ROUTE"]
        .astype(str)
        .isin(selected_routes)
    ]

# ============================================================
# KPI CALCULATIONS
# ============================================================

TOTAL_ACTUAL = (
    filtered_df["Actual_UCS"].sum()
    if "Actual_UCS" in filtered_df.columns
    else 0
)

TOTAL_TARGET = (
    filtered_df["SOP_UCS"].sum()
    if "SOP_UCS" in filtered_df.columns
    else 0
)

TOTAL_LY = (
    filtered_df["LY_UCS"].sum()
    if "LY_UCS" in filtered_df.columns
    else 0
)

ACHIEVEMENT = (
    (TOTAL_ACTUAL / TOTAL_TARGET) * 100
    if TOTAL_TARGET != 0 else 0
)

GROWTH = (
    ((TOTAL_ACTUAL - TOTAL_LY) / TOTAL_LY) * 100
    if TOTAL_LY != 0 else 0
)

TOTAL_OUTLETS = (
    filtered_df["Customer_Name"].nunique()
    if "Customer_Name" in filtered_df.columns
    else 0
)

TOTAL_ROUTES = (
    filtered_df["ROUTE"].nunique()
    if "ROUTE" in filtered_df.columns
    else 0
)

# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 KPI SUMMARY")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "TOTAL SALES",
    f"{TOTAL_ACTUAL:,.0f}"
)

col2.metric(
    "TARGET",
    f"{TOTAL_TARGET:,.0f}"
)

col3.metric(
    "ACH %",
    f"{ACHIEVEMENT:.2f}%"
)

col4.metric(
    "VS LY",
    f"{GROWTH:.2f}%"
)

col5.metric(
    "OUTLETS",
    f"{TOTAL_OUTLETS}"
)

col6.metric(
    "ROUTES",
    f"{TOTAL_ROUTES}"
)

st.markdown("---")

# ============================================================
# CHARTS ROW 1
# ============================================================

chart1, chart2 = st.columns(2)

# ============================================================
# ROUTE PERFORMANCE
# ============================================================

with chart1:

    st.subheader("📈 Route Performance")

    if (
        "ROUTE" in filtered_df.columns
        and "Actual_UCS" in filtered_df.columns
    ):

        route_summary = (
            filtered_df.groupby("ROUTE")[
                ["Actual_UCS", "SOP_UCS"]
            ]
            .sum()
            .reset_index()
        )

        fig_route = px.bar(
            route_summary,
            x="ROUTE",
            y=["Actual_UCS", "SOP_UCS"],
            barmode="group",
            template="plotly_dark"
        )

        fig_route.update_layout(
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_route,
            use_container_width=True
        )

# ============================================================
# TOP CUSTOMERS
# ============================================================

with chart2:

    st.subheader("🏆 Top Customers")

    if (
        "Customer_Name" in filtered_df.columns
        and "Actual_UCS" in filtered_df.columns
    ):

        top_customer = (
            filtered_df.groupby("Customer_Name")[
                "Actual_UCS"
            ]
            .sum()
            .reset_index()
            .sort_values(
                by="Actual_UCS",
                ascending=False
            )
            .head(10)
        )

        fig_customer = px.bar(
            top_customer,
            x="Actual_UCS",
            y="Customer_Name",
            orientation="h",
            template="plotly_dark"
        )

        fig_customer.update_layout(
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_customer,
            use_container_width=True
        )

# ============================================================
# CHARTS ROW 2
# ============================================================

chart3, chart4 = st.columns(2)

# ============================================================
# ACHIEVEMENT GAUGE
# ============================================================

with chart3:

    st.subheader("🎯 Achievement Gauge")

    fig_gauge = go.Figure(go.Indicator(

        mode="gauge+number",

        value=ACHIEVEMENT,

        title={
            "text": "Achievement %"
        },

        gauge={

            "axis": {
                "range": [0, 150]
            },

            "bar": {
                "color": "red"
            },

            "steps": [

                {
                    "range": [0, 70],
                    "color": "gray"
                },

                {
                    "range": [70, 100],
                    "color": "orange"
                },

                {
                    "range": [100, 150],
                    "color": "green"
                }
            ]
        }
    ))

    fig_gauge.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

# ============================================================
# PIE CHART
# ============================================================

with chart4:

    st.subheader("🥧 Achievement Distribution")

    pie_df = pd.DataFrame({

        "Category": [
            "Actual",
            "Remaining"
        ],

        "Value": [
            TOTAL_ACTUAL,
            max(TOTAL_TARGET - TOTAL_ACTUAL, 0)
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
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📋 Outlet Performance Table")

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

st.markdown(
    """
    <center>
        <p style='color:gray;'>
        Advanced Dynamic Dashboard • Powered by Streamlit + Plotly
        </p>
    </center>
    """,
    unsafe_allow_html=True
)
