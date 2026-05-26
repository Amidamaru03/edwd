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

[data-testid="stSidebar"] {
    background-color: #111827;
}

.kpi-card {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    margin-bottom: 10px;
}

.kpi-title {
    font-size: 14px;
    opacity: 0.8;
}

.kpi-value {
    font-size: 30px;
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
    "Upload Excel or CSV File",
    type=["xlsx", "xls", "csv"]
)

# =========================================================
# MAIN PROCESS
# =========================================================
if uploaded_file is not None:

    try:

        # =================================================
        # READ FILE WITHOUT HEADER
        # =================================================
        if uploaded_file.name.endswith(".csv"):
            temp_df = pd.read_csv(uploaded_file, header=None)
        else:
            temp_df = pd.read_excel(uploaded_file, header=None)

        # =================================================
        # FIND HEADER ROW
        # =================================================
        header_row = 0

        for i in range(len(temp_df)):

            row_values = (
                temp_df.iloc[i]
                .fillna("")
                .astype(str)
                .str.upper()
                .tolist()
            )

            row_text = " ".join([str(x) for x in row_values])

            if (
                "CUSTOMER" in row_text
                and "SNOP" in row_text
            ):
                header_row = i
                break

        # =================================================
        # RESET FILE POINTER
        # =================================================
        uploaded_file.seek(0)

        # =================================================
        # READ FILE USING DETECTED HEADER
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
        # AUTO RENAME COLUMNS
        # =================================================
        rename_map = {}

        for col in df.columns:

            col_upper = str(col).upper()

            if "CUSTOMER" in col_upper and "NAME" in col_upper:
                rename_map[col] = "Customer Name"

            elif "SNOP" in col_upper:
                rename_map[col] = "SNOP"

            elif "TOTAL UCS" in col_upper or "UCS" in col_upper:
                rename_map[col] = "TOTAL UCS"

            elif "ACV" in col_upper:
                rename_map[col] = "ACV VS S7OP"

            elif "VARIANCE" in col_upper:
                rename_map[col] = "VARIANCE TO HIT"

        df.rename(columns=rename_map, inplace=True)

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
Missing Columns:
{missing_cols}

Found Columns:
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

        # =================================================
        # SIDEBAR FILTERS
        # =================================================
        st.sidebar.header("🔍 Filters")

        customer_filter = st.sidebar.multiselect(
            "Customer Name",
            options=sorted(df["Customer Name"].dropna().unique()),
            default=sorted(df["Customer Name"].dropna().unique())
        )

        # =================================================
        # FILTER DATA
        # =================================================
        filtered_df = df[
            df["Customer Name"].isin(customer_filter)
        ]

        # =================================================
        # KPI CALCULATIONS
        # =================================================
        total_customers = filtered_df["Customer Name"].nunique()
        total_ucs = filtered_df["TOTAL UCS"].sum()
        total_snop = filtered_df["SNOP"].sum()
        total_variance = filtered_df["VARIANCE TO HIT"].sum()
        avg_acv = filtered_df["ACV VS S7OP"].mean()

        # =================================================
        # KPI SECTION
        # =================================================
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

        # =================================================
        # SUMMARY TABLE
        # =================================================
        summary = filtered_df.groupby(
            "Customer Name",
            as_index=False
        ).agg({
            "TOTAL UCS": "sum",
            "SNOP": "sum",
            "VARIANCE TO HIT": "sum",
            "ACV VS S7OP": "mean"
        })

        summary = summary.sort_values(
            by="TOTAL UCS",
            ascending=False
        )

        # =================================================
        # CHARTS
        # =================================================
        st.markdown("## 📊 Analytics")

        c1, c2 = st.columns(2)

        # BAR CHART
        fig_bar = px.bar(
            summary.head(10),
            x="TOTAL UCS",
            y="Customer Name",
            orientation="h",
            title="Top Customers by TOTAL UCS",
            text_auto=True
        )

        c1.plotly_chart(fig_bar, use_container_width=True)

        # SCATTER CHART
        fig_scatter = px.scatter(
            summary,
            x="SNOP",
            y="TOTAL UCS",
            size="VARIANCE TO HIT",
            color="ACV VS S7OP",
            hover_name="Customer Name",
            title="SNOP vs TOTAL UCS"
        )

        c2.plotly_chart(fig_scatter, use_container_width=True)

        # =================================================
        # HEATMAP
        # =================================================
        st.markdown("### 🔥 Variance Heatmap")

        heatmap_df = summary.pivot_table(
            values="VARIANCE TO HIT",
            index="Customer Name"
        )

        fig_heat = px.imshow(
            heatmap_df,
            aspect="auto"
        )

        st.plotly_chart(fig_heat, use_container_width=True)

        # =================================================
        # GAUGE CHART
        # =================================================
        g1, g2 = st.columns(2)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_acv,
            title={'text': "ACV VS S7OP"},
            gauge={
                'axis': {'range': [0, 150]}
            }
        ))

        g1.plotly_chart(fig_gauge, use_container_width=True)

        # PIE CHART
        fig_pie = px.pie(
            summary.head(10),
            names="Customer Name",
            values="TOTAL UCS",
            hole=0.5,
            title="Customer Contribution"
        )

        g2.plotly_chart(fig_pie, use_container_width=True)

        # =================================================
        # BUSINESS INSIGHTS
        # =================================================
        st.markdown("## 🤖 Business Insights")

        if len(summary) > 0:

            best_customer = summary.iloc[0]["Customer Name"]
            worst_customer = summary.iloc[-1]["Customer Name"]

            st.info(f"""
✅ Best Performing Customer:
{best_customer}

⚠️ Lowest Performing Customer:
{worst_customer}

📊 Focus on reducing variance and improving UCS conversion.

🚀 Improve low-performing accounts to increase overall execution.
""")

        # =================================================
        # DATA TABLE
        # =================================================
        st.markdown("## 📋 Dataset")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500
        )

        # =================================================
        # DOWNLOAD BUTTON
        # =================================================
        output = BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False)

        st.download_button(
            label="📥 Download Filtered Data",
            data=output.getvalue(),
            file_name="filtered_dashboard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload an Excel or CSV file to begin.")
