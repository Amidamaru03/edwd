import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Executive Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #0f172a;
    color: white;
}

.block-container {
    padding-top: 1rem;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.kpi-card {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    transition: 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);
}

.kpi-title {
    font-size: 14px;
    opacity: 0.8;
}

.kpi-value {
    font-size: 32px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("📊 Executive Sales Performance Dashboard")
st.caption("Interactive enterprise analytics dashboard")

# =========================================================
# FILE UPLOADER
# =========================================================
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls", "csv"]
)

# =========================================================
# PROCESS FILE
# =========================================================
if uploaded_file is not None:

    with st.spinner("Processing file..."):

        # =================================================
        # READ FILE WITHOUT HEADER
        # =================================================
        if uploaded_file.name.endswith(".csv"):
            temp_df = pd.read_csv(uploaded_file, header=None)
        else:
            temp_df = pd.read_excel(uploaded_file, header=None)

        # =================================================
        # AUTO DETECT HEADER ROW
        # =================================================
        header_row = None

        for i in range(len(temp_df)):

            row_values = temp_df.iloc[i].astype(str).str.upper().tolist()

            if (
                any("CUSTOMER" in val for val in row_values)
                and any("SNOP" in val for val in row_values)
            ):
                header_row = i
                break

        # =================================================
        # VALIDATE HEADER
        # =================================================
        if header_row is None:

            st.error("""
            Could not detect the correct header row.

            Required columns:
            - Customer Name
            - SNOP
            - TOTAL UCS
            - ACV VS S7OP
            - VARIANCE TO HIT
            """)

            st.stop()

        # =================================================
        # RELOAD FILE USING DETECTED HEADER
        # =================================================
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, header=header_row)
        else:
            df = pd.read_excel(uploaded_file, header=header_row)

        # =================================================
        # CLEAN COLUMN NAMES
        # =================================================
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace("\n", " ", regex=False)
            .str.replace("\r", " ", regex=False)
        )

        # =================================================
        # AUTO MAP COLUMNS
        # =================================================
        column_mapping = {}

        for col in df.columns:

            col_upper = col.upper()

            if "CUSTOMER" in col_upper and "NAME" in col_upper:
                column_mapping[col] = "Customer Name"

            elif "SNOP" in col_upper:
                column_mapping[col] = "SNOP"

            elif "TOTAL UCS" in col_upper or "UCS" in col_upper:
                column_mapping[col] = "TOTAL UCS"

            elif "ACV" in col_upper:
                column_mapping[col] = "ACV VS S7OP"

            elif "VARIANCE" in col_upper:
                column_mapping[col] = "VARIANCE TO HIT"

        df = df.rename(columns=column_mapping)

        # =================================================
        # REQUIRED COLUMNS
        # =================================================
        required_cols = [
            "Customer Name",
            "SNOP",
            "TOTAL UCS",
            "ACV VS S7OP",
            "VARIANCE TO HIT"
        ]

        missing_cols = [
            col for col in required_cols
            if col not in df.columns
        ]

        if missing_cols:

            st.error(f"""
            Missing columns:
            {missing_cols}

            Current columns found:
            {list(df.columns)}
            """)

            st.stop()

        # =================================================
        # NUMERIC CONVERSION
        # =================================================
        numeric_cols = [
            "SNOP",
            "TOTAL UCS",
            "ACV VS S7OP",
            "VARIANCE TO HIT"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    st.success("File uploaded successfully!")

    # =========================================================
    # SIDEBAR FILTERS
    # =========================================================
    st.sidebar.header("🔍 Dashboard Filters")

    selected_customers = st.sidebar.multiselect(
        "Customer Name",
        options=sorted(df["Customer Name"].dropna().unique()),
        default=sorted(df["Customer Name"].dropna().unique())
    )

    timeline = st.sidebar.selectbox(
        "Timeline",
        ["Monthly", "Quarterly", "Yearly"]
    )

    # =========================================================
    # FILTER DATA
    # =========================================================
    filtered_df = df[
        df["Customer Name"].isin(selected_customers)
    ]

    # =========================================================
    # KPI CALCULATIONS
    # =========================================================
    total_customers = filtered_df["Customer Name"].nunique()
    total_ucs = filtered_df["TOTAL UCS"].sum()
    total_snop = filtered_df["SNOP"].sum()
    total_variance = filtered_df["VARIANCE TO HIT"].sum()
    avg_acv = filtered_df["ACV VS S7OP"].mean()

    # =========================================================
    # KPI CARDS
    # =========================================================
    st.markdown("## 📌 KPI Overview")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">👥 Total Customers</div>
            <div class="kpi-value">{total_customers:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📦 Total UCS</div>
            <div class="kpi-value">{total_ucs:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">🎯 Total SNOP</div>
            <div class="kpi-value">{total_snop:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⚠️ Variance To Hit</div>
            <div class="kpi-value">{total_variance:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 Avg ACV VS S7OP</div>
            <div class="kpi-value">{avg_acv:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # CUSTOMER SUMMARY
    # =========================================================
    customer_summary = filtered_df.groupby(
        "Customer Name",
        as_index=False
    ).agg({
        "TOTAL UCS": "sum",
        "SNOP": "sum",
        "VARIANCE TO HIT": "sum",
        "ACV VS S7OP": "mean"
    })

    customer_summary = customer_summary.sort_values(
        by="TOTAL UCS",
        ascending=False
    )

    # =========================================================
    # CHARTS
    # =========================================================
    st.markdown("## 📊 Advanced Analytics")

    c1, c2 = st.columns(2)

    # BAR CHART
    fig_bar = px.bar(
        customer_summary.head(10),
        x="TOTAL UCS",
        y="Customer Name",
        orientation="h",
        title="Top Customers by TOTAL UCS",
        text_auto=True
    )

    c1.plotly_chart(fig_bar, use_container_width=True)

    # SCATTER CHART
    fig_scatter = px.scatter(
        customer_summary,
        x="SNOP",
        y="TOTAL UCS",
        size="VARIANCE TO HIT",
        color="ACV VS S7OP",
        hover_name="Customer Name",
        title="SNOP vs TOTAL UCS"
    )

    c2.plotly_chart(fig_scatter, use_container_width=True)

    # =========================================================
    # HEATMAP
    # =========================================================
    st.markdown("### 🔥 Variance Heatmap")

    heatmap_df = customer_summary.pivot_table(
        values="VARIANCE TO HIT",
        index="Customer Name"
    )

    fig_heatmap = px.imshow(
        heatmap_df,
        aspect="auto",
        title="Customer Variance Heatmap"
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # =========================================================
    # GAUGE + DONUT
    # =========================================================
    g1, g2 = st.columns(2)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_acv,
        title={'text': "ACV VS S7OP Performance"},
        gauge={
            'axis': {'range': [0, 150]},
            'steps': [
                {'range': [0, 60], 'color': "red"},
                {'range': [60, 100], 'color': "yellow"},
                {'range': [100, 150], 'color': "green"}
            ],
            'bar': {'color': "blue"}
        }
    ))

    g1.plotly_chart(fig_gauge, use_container_width=True)

    fig_donut = px.pie(
        customer_summary.head(10),
        names="Customer Name",
        values="TOTAL UCS",
        hole=0.5,
        title="Customer Contribution"
    )

    g2.plotly_chart(fig_donut, use_container_width=True)

    # =========================================================
    # AI INSIGHTS
    # =========================================================
    st.markdown("## 🤖 AI Business Insights")

    best_customer = customer_summary.iloc[0]
    worst_customer = customer_summary.iloc[-1]

    below_target = customer_summary[
        customer_summary["ACV VS S7OP"] < 100
    ].shape[0]

    st.info(f"""
    ✅ Best Performing Customer:
    {best_customer['Customer Name']}
    with TOTAL UCS of {best_customer['TOTAL UCS']:,.0f}

    ⚠️ Lowest Performing Customer:
    {worst_customer['Customer Name']}
    with TOTAL UCS of {worst_customer['TOTAL UCS']:,.0f}

    📉 Customers Below Target:
    {below_target}

    🚀 Recommendations:
    - Improve UCS conversion
    - Focus on low-performing customers
    - Monitor variance closely
    - Increase support for weak accounts
    """)

    # =========================================================
    # DATA TABLE
    # =========================================================
    st.markdown("## 📋 Detailed Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

    # =========================================================
    # DOWNLOAD BUTTON
    # =========================================================
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_df.to_excel(writer, index=False)

    st.download_button(
        label="📥 Download Filtered Data",
        data=output.getvalue(),
        file_name="filtered_sales_dashboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Please upload an Excel or CSV file to begin.")
