import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="BD Batangas Daily Sales Dashboard",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

.title {
    font-size: 38px;
    font-weight: bold;
    color: white;
    text-align: center;
    padding: 15px;
    border-radius: 12px;
    background: linear-gradient(90deg, #b91c1c, #ef4444);
    margin-bottom: 20px;
}

.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #1f2937;
}

.card-title {
    color: #9ca3af;
    font-size: 14px;
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
    margin-top: 25px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    '<div class="title">BD BATANGAS DAILY SALES DASHBOARD</div>',
    unsafe_allow_html=True
)

# =====================================================
# FILE UPLOADER
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Excel Dashboard File",
    type=["xlsx", "xlsm"]
)

if uploaded_file is not None:

    try:

        # =====================================================
        # LOAD SHEETS
        # =====================================================

        xl = pd.ExcelFile(uploaded_file)

        st.sidebar.header("AVAILABLE SHEETS")

        st.sidebar.write(xl.sheet_names)

        # Load sheets safely
        dashboard_df = pd.read_excel(uploaded_file, sheet_name="DASHBOARD")

        outlet_df = pd.read_excel(uploaded_file, sheet_name="OUTLETS")

        plan_df = pd.read_excel(uploaded_file, sheet_name="PLANSHIPMENTS")

        # =====================================================
        # SIDEBAR FILTER
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
                outlet_df[route_col].astype(str)
                == selected_route
            ]

        else:

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

            if str(col).upper() in [
                x.upper() for x in possible_sales_cols
            ]:
                sales_col = col
                break

        if sales_col is None:

            numeric_cols = plan_df.select_dtypes(
                include="number"
            ).columns

            if len(numeric_cols) > 0:
                sales_col = numeric_cols[-1]

        # =====================================================
        # KPI VALUES
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
            ("MAX SALES", f"{max_sales:,.0f}")
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
        # DAILY SALES CHART
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

            plan_df[date_col] = pd.to_datetime(
                plan_df[date_col]
            )

            daily_sales = (
                plan_df.groupby(date_col)[sales_col]
                .sum()
                .reset_index()
            )

            fig_bar = px.bar(
                daily_sales,
                x=date_col,
                y=sales_col,
                template="plotly_dark"
            )

            fig_bar.update_layout(
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                height=400
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True
            )

        # =====================================================
        # PRODUCT MIX
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

            st.plotly_chart(
                fig_donut,
                use_container_width=True
            )

        # =====================================================
        # CUSTOMER TABLE
        # =====================================================

        st.markdown(
            '<div class="section-title">Customer Performance</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            filtered_outlets,
            use_container_width=True,
            height=450
        )

        # =====================================================
        # ACHIEVEMENT GAUGE
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

        st.plotly_chart(
            fig_gauge,
            use_container_width=True
        )

        # =====================================================
        # FOOTER
        # =====================================================

        st.markdown("---")

        st.markdown("""
        <center style='color:gray'>
        Generated from Excel Dashboard using Python + Streamlit
        </center>
        """, unsafe_allow_html=True)

    except Exception as e:

        st.error(f"Error loading Excel file: {e}")

else:

    st.info("Please upload your Excel dashboard file.")
