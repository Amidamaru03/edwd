import streamlit as st
import pandas as pd
import plotly.express as px
import base64

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
# BACKGROUND IMAGE FUNCTION
# =====================================================

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

        /* DARK OVERLAY */
        .stApp:before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            background: rgba(0,0,0,0.60);
            z-index: -1;
        }}

        /* GLOBAL TEXT */
        html, body, [class*="css"] {{
            font-family: 'Segoe UI', sans-serif;
            color: white;
        }}

        /* MAIN CONTAINER */
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}

        /* KPI CARDS */
        .metric-card {{
            background: rgba(0,0,0,0.65);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }}

        .metric-title {{
            font-size: 14px;
            color: #d1d5db;
        }}

        .metric-value {{
            font-size: 30px;
            font-weight: bold;
            color: white;
        }}

        /* SIDEBAR */
        section[data-testid="stSidebar"] {{
            background: rgba(0,0,0,0.75);
            backdrop-filter: blur(15px);
        }}

        /* TABLE */
        [data-testid="stDataFrame"] {{
            background: rgba(0,0,0,0.55);
            border-radius: 16px;
            overflow: hidden;
        }}

        /* BUTTONS */
        .stButton button,
        .stDownloadButton button {{
            background: linear-gradient(135deg, #ff0000, #990000);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1rem;
            font-weight: bold;
        }}

        /* INPUTS */
        .stTextInput > div > div > input {{
            background-color: rgba(255,255,255,0.08);
            color: white;
        }}

        /* MOBILE */
        @media (max-width: 768px) {{

            .metric-value {{
                font-size: 22px;
            }}

            h1 {{
                font-size: 28px !important;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# LOAD BACKGROUND IMAGE
# =====================================================

add_bg_from_local("npls.jpeg")

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
# PROCESS FILE
# =====================================================

if uploaded_file:

    # LOAD EXCEL
    df = pd.read_excel(uploaded_file)

    # CLEAN DATA
    df.columns = df.columns.astype(str).str.strip()

    # NUMERIC COLUMNS
    numeric_cols = [
        'SNOP',
        'TOTAL UCS',
        'ACV VS S7OP',
        'VARIANCE TO HIT'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

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

    # =====================================================
    # KPI CALCULATIONS
    # =====================================================

    total_ucs = filtered_df['TOTAL UCS'].sum() if 'TOTAL UCS' in filtered_df.columns else 0
    total_snop = filtered_df['SNOP'].sum() if 'SNOP' in filtered_df.columns else 0
    total_variance = filtered_df['VARIANCE TO HIT'].sum() if 'VARIANCE TO HIT' in filtered_df.columns else 0

    avg_acv = (
        filtered_df['ACV VS S7OP'].mean()
        if 'ACV VS S7OP' in filtered_df.columns
        else 0
    )

    # =====================================================
    # KPI SECTION
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TOTAL UCS</div>
            <div class="metric-value">{total_ucs:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TOTAL SNOP</div>
            <div class="metric-value">{total_snop:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TOTAL VARIANCE</div>
            <div class="metric-value">{total_variance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">AVG ACV VS S7OP</div>
            <div class="metric-value">{avg_acv:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # =====================================================
    # CHARTS
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
            title='🏆 Top Customers',
            text_auto='.2s'
        )

        fig1.update_layout(
            template='plotly_dark',
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        chart1.plotly_chart(fig1, use_container_width=True)

    # PIE CHART
    if 'Customer Name' in filtered_df.columns and 'TOTAL UCS' in filtered_df.columns:

        pie_data = (
            filtered_df.groupby('Customer Name')['TOTAL UCS']
            .sum()
            .head(5)
            .reset_index()
        )

        fig2 = px.pie(
            pie_data,
            names='Customer Name',
            values='TOTAL UCS',
            hole=0.5,
            title='📊 Customer Distribution'
        )

        fig2.update_layout(
            template='plotly_dark',
            height=450,
            paper_bgcolor='rgba(0,0,0,0)'
        )

        chart2.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # SEARCH
    # =====================================================

    st.subheader("📋 Smart Data Explorer")

    search = st.text_input("🔍 Search data")

    display_df = filtered_df.copy()

    if search:

        mask = display_df.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)
        ).any(axis=1)

        display_df = display_df[mask]

    # =====================================================
    # DISPLAY DATA
    # =====================================================

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500
    )

    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name="sales_dashboard.csv",
        mime="text/csv"
    )

    # =====================================================
    # AI INSIGHTS
    # =====================================================

    st.markdown("---")

    st.subheader("🧠 AI Smart Insights")

    try:
        best_customer = top_customers.iloc[0]['Customer Name']
        best_value = top_customers.iloc[0]['TOTAL UCS']

        st.success(
            f"🔥 Top customer is {best_customer} with {best_value:,.2f} TOTAL UCS."
        )

        if total_variance < 0:
            st.error("⚠ Sales variance is below target.")
        else:
            st.success("✅ Sales performance is above target.")

    except:
        st.warning("Upload valid sales data to generate insights.")

else:

    st.info("📂 Upload an Excel file to launch the dashboard.")

