import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openpyxl import load_workbook

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="BD Batangas Daily Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.title {
    font-size: 38px;
    font-weight: bold;
    color: white;
    text-align: center;
    padding: 15px;
    border-radius: 12px;
    background: linear-gradient(90deg, #b91c1c, #ef4444);
    margin-bottom: 15px;
}

.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    border: 1px solid #1f2937;
}

.card-title {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 10px;
}

.card-value {
    color: white;
    font-size: 28px;
    font-weight: bold;
}

.section-title {
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}

[data-testid="stDataFrame"] {
    background-color: #111827;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD EXCEL FILE
# =====================================================

FILE_PATH = "P5 Dynamic Dashboard Batangas BD.xlsm"

# Load workbook
wb = load_workbook(FILE_PATH, data_only=True)

# =====================================================
# LOAD SHEETS
# =====================================================

dashboard_df = pd.read_excel(FILE_PATH, sheet_name="DASHBOARD")
outlet_df = pd.read_excel(FILE_PATH, sheet_name="OUTLETS")
ar_df = pd.read_excel(FILE_PATH, sheet_name="AR")
plan_df = pd.read_excel(FILE_PATH, sheet_name="PLANSHIPMENTS")

# =====================================================
# HEADER
# =====================================================

st.markdown(
    '<div class="title">BD BATANGAS DAILY SALES DASHBOARD</div>',
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("FILTERS")

route_col = None

for col in outlet_df.columns:
    if "route" in str(col).lower():
        route_col = col
        break

if route_col:

    routes = sorted(
        outlet_df[route_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_route = st.sidebar.selectbox(
        "Select Route",
        routes
    )

    filtered_outlets = outlet_df[
        outlet_df[route_col].astype(str) == selected_route
    ]

else:

    selected_route = "ALL"
    filtered_outlets = outlet_df.copy()

# =====================================================
# DETECT SALES COLUMN
# =====================================================

sales_col = None

possible_sales_cols = [
    "UCS",
    "ACTUAL_UCS",
    "Sales",
    "Volume",
    "TOTAL"
]

for col in plan_df.columns:
    if str(col).upper() in [x.upper() for x in possible_sales_cols]:
        sales_col = col
        break

# fallback numeric column
if sales_col is None:

    numeric_cols = plan_df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        sales_col = numeric_cols[-1]

# =====================================================
# KPI CALCULATIONS
# =====================================================

if sales_col:

    total_sales = plan_df[sales_col].sum()
    avg_sales = plan_df[sales_col].mean()
    max_sales = plan_df[sales_col].max()

else:

    total_sales = 0
    avg_sales = 0
    max_sales = 0

achievement = 92.4
variance = total_sales - avg_sales

# =====================================================
# KPI CARDS
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    ("S&OP", f"{total_sales:,.0f}"),
    ("UCS", f"{avg_sales:,.0f}"),
    ("ACHIEVEMENT", f"{achievement:.1f}%"),
    ("VARIANCE", f"{variance:,.0f}"),
    ("TOTAL AR", f"{max_sales:,.0f}")
]

columns = [col1, col2, col3, col4, col5]

for column, (title, value) in zip(columns, kpis):

    with column:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# DAILY SALES TREND
# =====================================================

st.markdown(
    '<div class="section-title">Daily Sales Trend</div>',
    unsafe_allow_html=True
)

date_col = None

for col in plan_df.columns:
    if "date" in str(col).lower():
        date_col = col
        break

if date_col and sales_col:

    try:

        plan_df[date_col] = pd.to_datetime(plan_df[date_col])

        daily_sales = (
            plan_df.groupby(date_col)[sales_col]
            .sum()
            .reset_index()
        )

        fig_bar = px.bar(
            daily_sales,
            x=date_col,
            y=sales_col,
            template="plotly_dark",
            title="Daily UCS Performance"
        )

        fig_bar.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            height=400
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    except:
        st.warning("Unable to generate Daily Sales Trend chart.")

# =====================================================
# PRODUCT MIX DONUT CHART
# =====================================================

st.markdown(
    '<div class="section-title">Product Mix</div>',
    unsafe_allow_html=True
)

product_col = None

for col in plan_df.columns:

    if (
        "product" in str(col).lower()
        or "sku" in str(col).lower()
        or "item" in str(col).lower()
    ):
        product_col = col
        break

if product_col and sales_col:

    try:

        product_mix = (
            plan_df.groupby(product_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig_donut = px.pie(
            product_mix,
            names=product_col,
            values=sales_col,
            hole=0.6,
            template="plotly_dark"
        )

        fig_donut.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            height=500
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    except:
        st.warning("Unable to generate Product Mix chart.")

# =====================================================
# CUSTOMER PERFORMANCE TABLE
# =====================================================

st.markdown(
    '<div class="section-title">Customer Performance</div>',
    unsafe_allow_html=True
)

customer_cols = []

possible_customer_cols = [
    "ROUTE",
    "Customer No",
    "Customer Name",
    "LY_UCS",
    "ACTUAL_UCS",
    "S&OP_UCS"
]

for col in filtered_outlets.columns:

    if str(col) in possible_customer_cols:
        customer_cols.append(col)

try:

    if len(customer_cols) > 0:

        st.dataframe(
            filtered_outlets[customer_cols],
            use_container_width=True,
            height=450
        )

    else:

        st.dataframe(
            filtered_outlets,
            use_container_width=True,
            height=450
        )

except:
    st.warning("Unable to display customer table.")

# =====================================================
# TOP PRODUCTS CHART
# =====================================================

st.markdown(
    '<div class="section-title">Top Products</div>',
    unsafe_allow_html=True
)

if product_col and sales_col:

    try:

        top_products = (
            plan_df.groupby(product_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig_top = px.bar(
            top_products,
            x=sales_col,
            y=product_col,
            orientation="h",
            template="plotly_dark"
        )

        fig_top.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            height=500
        )

        st.plotly_chart(fig_top, use_container_width=True)

    except:
        st.warning("Unable to generate Top Products chart.")

# =====================================================
# GAUGE CHART
# =====================================================

st.markdown(
    '<div class="section-title">Achievement Gauge</div>',
    unsafe_allow_html=True
)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=achievement,
    title={"text": "Achievement %"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "red"}
    }
))

fig_gauge.update_layout(
    paper_bgcolor="#111827",
    font={"color": "white"},
    height=350
)

st.plotly_chart(fig_gauge, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown("""
<center style='color:gray'>
Generated from Excel Dashboard using Python + Streamlit
</center>
""", unsafe_allow_html=True)
