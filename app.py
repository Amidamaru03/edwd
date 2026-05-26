import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================
st.markdown("""
<style>

.main {
    background-color: #0f172a;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.kpi-card {
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    padding: 20px;
    border-radius: 18px;
    color: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    transition: 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);
}

.big-font {
    font-size: 32px;
    font-weight: bold;
}

.small-font {
    font-size: 14px;
    opacity: 0.8;
}

.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# HEADER
# =========================================
st.title("📊 Executive Sales Performance Dashboard")
st.markdown("Interactive enterprise analytics dashboard")

# =========================================
# FILE UPLOAD
# =========================================
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:

    with st.spinner("Processing file..."):

        # READ FILE
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # CLEAN COLUMNS
        df.columns = df.columns.str.strip()

        # REQUIRED COLUMNS
        required_cols = [
            "Customer Name",
            "SNOP",
            "TOTAL UCS",
            "ACV VS S7OP",
            "VARIANCE TO HIT"
        ]

        # VALIDATE
        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        # NUMERIC CONVERSION
        numeric_cols = [
            "SNOP",
            "TOTAL UCS",
            "ACV VS S7OP",
            "VARIANCE TO HIT"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    st.success("File uploaded successfully!")

    # =========================================
    # SIDEBAR FILTERS
    # =========================================
    st.sidebar.header("🔍 Filters")

    customer_filter = st.sidebar.multiselect(
        "Customer Name",
        options=df["Customer Name"].unique(),
        default=df["Customer Name"].unique()
    )

    timeline = st.sidebar.selectbox(
        "Timeline",
        ["Monthly", "Quarterly", "Yearly"]
    )

    dark_mode = st.sidebar.toggle("Dark Mode", value=True)

    # FILTER DATA
    filtered_df = df[
        df["Customer Name"].isin(customer_filter)
    ]

    # =========================================
    # KPI CALCULATIONS
    # =========================================
    total_customers = filtered_df["Customer Name"].nunique()
    total_ucs = filtered_df["TOTAL UCS"].sum()
    total_snop = filtered_df["SNOP"].sum()
    total_variance = filtered_df["VARIANCE TO HIT"].sum()
    avg_acv = filtered_df["ACV VS S7OP"].mean()

    # =========================================
    # KPI SECTION
    # =========================================
    st.markdown("## 📌 KPI Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="small-font">👥 Total Customers</div>
            <div class="big-font">{total_customers:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="small-font">📦 Total UCS</div>
            <div class="big-font">{total_ucs:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="small-font">🎯 Total SNOP</div>
            <div class="big-font">{total_snop:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="small-font">⚠️ Variance To Hit</div>
            <div class="big-font">{total_variance:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="small-font">📈 Avg ACV VS S7OP</div>
            <div class="big-font">{avg_acv:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================
    # CHARTS
    # =========================================
    st.markdown("## 📊 Advanced Analytics")

    chart1, chart2 = st.columns(2)

    # =========================================
    # BAR CHART
    # =========================================
    top_customers = filtered_df.groupby(
        "Customer Name"
    )["TOTAL UCS"].sum().reset_index()

    top_customers = top_customers.sort_values(
        by="TOTAL UCS",
        ascending=False
    ).head(10)

    fig_bar = px.bar(
        top_customers,
        x="TOTAL UCS",
        y="Customer Name",
        orientation='h',
        title="Top Customers by TOTAL UCS",
        text_auto=True
    )

    chart1.plotly_chart(fig_bar, use_container_width=True)

    # =========================================
    # SCATTER CHART
    # =========================================
    fig_scatter = px.scatter(
        filtered_df,
        x="SNOP",
        y="TOTAL UCS",
        size="VARIANCE TO HIT",
        color="ACV VS S7OP",
        hover_name="Customer Name",
        title="SNOP vs TOTAL UCS"
    )

    chart2.plotly_chart(fig_scatter, use_container_width=True)

    # =========================================
    # HEATMAP
    # =========================================
    st.markdown("### 🔥 Variance Heatmap")

    heatmap_data = filtered_df.pivot_table(
        values="VARIANCE TO HIT",
        index="Customer Name",
        aggfunc='sum'
    )

    fig_heat = px.imshow(
        heatmap_data,
        aspect="auto",
        title="Variance To Hit Heatmap"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # =========================================
    # GAUGE CHART
    # =========================================
    gauge_col1, gauge_col2 = st.columns(2)

    avg_performance = filtered_df["ACV VS S7OP"].mean()

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_performance,
        title={'text': "ACV VS S7OP Performance"},
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 100], 'color': "yellow"},
                {'range': [100, 150], 'color': "green"}
            ]
        }
    ))

    gauge_col1.plotly_chart(fig_gauge, use_container_width=True)

    # =========================================
    # DONUT CHART
    # =========================================
    fig_donut = px.pie(
        top_customers,
        values="TOTAL UCS",
        names="Customer Name",
        hole=0.5,
        title="Customer Contribution Distribution"
    )

    gauge_col2.plotly_chart(fig_donut, use_container_width=True)

    # =========================================
    # DEEP ANALYSIS
    # =========================================
    st.markdown("## 🤖 AI Business Insights")

    best_customer = top_customers.iloc[0]["Customer Name"]
    best_ucs = top_customers.iloc[0]["TOTAL UCS"]

    lowest_customer = top_customers.iloc[-1]["Customer Name"]
    lowest_ucs = top_customers.iloc[-1]["TOTAL UCS"]

    below_target = filtered_df[
        filtered_df["ACV VS S7OP"] < 100
    ].shape[0]

    st.info(f"""
    ✅ Best Performing Customer: {best_customer} with {best_ucs:,.0f} UCS

    ⚠️ Lowest Performing Customer: {lowest_customer} with {lowest_ucs:,.0f} UCS

    📉 Customers Below Target: {below_target}

    📊 Total UCS Concentration indicates strong dependency on top-performing customers.

    🚀 Recommendation:
    - Increase support for low-performing accounts
    - Focus on customers with high SNOP but low UCS conversion
    - Monitor variance closely to improve operational execution
    """)

    # =========================================
    # DATA TABLE
    # =========================================
    st.markdown("## 📋 Detailed Data Table")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

    # =========================================
    # DOWNLOAD FILTERED DATA
    # =========================================
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False)

    st.download_button(
        label="📥 Download Filtered Data",
        data=output.getvalue(),
        file_name="filtered_dashboard_data.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.info("Please upload an Excel file to begin.")
