
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
import base64

# =========================================
# FUNCTION TO ADD BACKGROUND IMAGE
# =========================================

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* OPTIONAL DARK OVERLAY */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55);
            z-index: -1;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<style>

.metric-card {
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(12px);
}

</style>
""", unsafe_allow_html=True)


# =========================================
# CALL FUNCTION
# =========================================

add_bg_from_local("npls.jpeg")

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI LIVE Sales Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* GLOBAL */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(to bottom right, #0f172a, #111827);
    color: white;
}

/* KPI CARDS */
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    transition: 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
}

.metric-title {
    font-size: 14px;
    color: #cbd5e1;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: white;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

/* BUTTONS */
.stButton button,
.stDownloadButton button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

/* MOBILE */
@media (max-width: 768px) {

    h1 {
        font-size: 28px !important;
        text-align: center;
    }

    .metric-value {
        font-size: 20px;
    }

    .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("🚀 AI-Powered LIVE Sales Dashboard")
st.caption("Enterprise Analytics • Real-Time Insights • Smart Performance Tracking")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📂 Upload Excel File",
    type=["xlsx", "xls"]
)

# =====================================================
# LOAD DATA
# =====================================================

if uploaded_file:

    # LOAD EXCEL
    df = pd.read_excel(uploaded_file, header=6)

    # CLEAN DATA
    df = df.dropna(how='all')
    df = df.loc[:, ~df.columns.isna()]
    df.columns = df.columns.astype(str).str.strip()

    # =====================================================
    # NUMERIC COLUMNS
    # =====================================================

    numeric_cols = [
        'S&OP',
        'SNOP',
        'TOTAL UCS',
        'ACV VS S7OP',
        'VARIANCE TO HIT'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # =====================================================
    # DATE FORMAT
    # =====================================================

    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================

    st.sidebar.header("⚡ Dashboard Filters")

    filtered_df = df.copy()

    # CUSTOMER FILTER
    if 'Customer Name' in df.columns:

        customer_filter = st.sidebar.multiselect(
            "Select Customer",
            options=sorted(df['Customer Name'].dropna().unique())
        )

        if customer_filter:
            filtered_df = filtered_df[
                filtered_df['Customer Name'].isin(customer_filter)
            ]

    # ROUTE FILTER
    if 'ROUTE' in df.columns:

        route_filter = st.sidebar.multiselect(
            "Select Route",
            options=sorted(df['ROUTE'].dropna().unique())
        )

        if route_filter:
            filtered_df = filtered_df[
                filtered_df['ROUTE'].isin(route_filter)
            ]

    # =====================================================
    # KPI CALCULATIONS
    # =====================================================

    total_ucs = filtered_df['TOTAL UCS'].sum() if 'TOTAL UCS' in filtered_df.columns else 0
    total_snop = filtered_df['SNOP'].sum() if 'SNOP' in filtered_df.columns else 0
    total_variance = filtered_df['VARIANCE TO HIT'].sum() if 'VARIANCE TO HIT' in filtered_df.columns else 0

    avg_acv = (
        filtered_df['ACV VS S7OP'].mean() * 100
        if 'ACV VS S7OP' in filtered_df.columns
        else 0
    )

    # =====================================================
    # KPI SECTION
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>TOTAL UCS</div>
            <div class='metric-value'>{total_ucs:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>TOTAL SNOP</div>
            <div class='metric-value'>{total_snop:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>TOTAL VARIANCE</div>
            <div class='metric-value'>{total_variance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>AVG ACV VS S7OP</div>
            <div class='metric-value'>{avg_acv:,.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # CHARTS SECTION
    # =====================================================

    chart1, chart2 = st.columns(2)

    # TOP CUSTOMERS
    if 'Customer Name' in filtered_df.columns and 'TOTAL UCS' in filtered_df.columns:

        top_customers = (
            filtered_df.groupby('Customer Name')['TOTAL UCS']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig1 = px.bar(
            top_customers,
            x='Customer Name',
            y='TOTAL UCS',
            text_auto='.2s',
            title='🏆 Top 10 Customers'
        )

        fig1.update_layout(
            template='plotly_dark',
            height=450
        )

        chart1.plotly_chart(fig1, use_container_width=True)

    # PARTNER MODEL PIE
    if 'PARTNER SUB MODEL' in filtered_df.columns and 'TOTAL UCS' in filtered_df.columns:

        partner_data = (
            filtered_df.groupby('PARTNER SUB MODEL')['TOTAL UCS']
            .sum()
            .reset_index()
        )

        fig2 = px.pie(
            partner_data,
            names='PARTNER SUB MODEL',
            values='TOTAL UCS',
            hole=0.45,
            title='📦 Partner Distribution'
        )

        fig2.update_layout(
            template='plotly_dark',
            height=450
        )

        chart2.plotly_chart(fig2, use_container_width=True)

    # =====================================================
    # ROUTE ANALYTICS
    # =====================================================

    if 'ROUTE' in filtered_df.columns and 'TOTAL UCS' in filtered_df.columns:

        route_data = (
            filtered_df.groupby('ROUTE')['TOTAL UCS']
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )

        fig3 = px.line(
            route_data,
            x='ROUTE',
            y='TOTAL UCS',
            markers=True,
            title='🚚 Route Performance'
        )

        fig3.update_layout(
            template='plotly_dark',
            height=500
        )

        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # =====================================================
    # SEARCH TABLE
    # =====================================================

    st.subheader("📋 Smart Data Explorer")

    search = st.text_input("🔍 Search entire database")

    display_df = filtered_df.copy()

    if search:

        mask = display_df.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)
        ).any(axis=1)

        display_df = display_df[mask]

    # =====================================================
    # FORMAT TABLE
    # =====================================================

    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(
                lambda x: f"{x:,.2f}" if pd.notnull(x) else ""
            )

    if 'ACV VS S7OP' in display_df.columns:
        display_df['ACV VS S7OP'] = display_df['ACV VS S7OP'].astype(str) + '%'

    # =====================================================
    # DISPLAY TABLE
    # =====================================================

    st.dataframe(
        display_df,
        use_container_width=True,
        height=600
    )

    # =====================================================
    # DOWNLOAD OPTIONS
    # =====================================================

    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label='⬇ Download CSV Report',
        data=csv,
        file_name='advanced_sales_dashboard.csv',
        mime='text/csv'
    )

    # =====================================================
    # AI INSIGHTS
    # =====================================================

    st.divider()

    st.subheader("🧠 AI Smart Insights")

    try:

        best_customer = top_customers.iloc[0]['Customer Name']
        best_value = top_customers.iloc[0]['TOTAL UCS']

        st.success(
            f"Top performing customer is {best_customer} with {best_value:,.2f} TOTAL UCS."
        )

        if total_variance < 0:
            st.error("Current sales variance is below target. Immediate recovery action recommended.")
        else:
            st.success("Sales performance is currently above target trajectory.")

    except:
        pass

else:

    st.info("📂 Upload an Excel file to launch the AI dashboard.")

