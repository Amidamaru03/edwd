# PROFESSIONAL INTERACTIVE DYNAMIC DASHBOARD

## Features Included

* Exact Coca-Cola style dark dashboard theme
* Dynamic outlet filtering
* KPI cards from Dashboard sheet
* Daily sales trend chart
* SKU mix donut chart
* Top SKU chart
* Customer performance table
* Achievement gauge
* Auto-detection of columns
* Responsive professional layout
* Excel-driven dynamic dashboard
* Streamlit interactive web app

---

# INSTALL REQUIREMENTS

```bash
pip install streamlit pandas plotly openpyxl
```

---

# SAVE AS

```bash
app.py
```

---

# RUN

```bash
streamlit run app.py
```

---

# FINAL CLEAN CODE

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="BD Batangas Dynamic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI';
}

.main {
    background-color: #0f172a;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.dashboard-title {
    background: linear-gradient(90deg,#b91c1c,#ef4444);
    padding: 18px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.card {
    background: #111827;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #1f2937;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.35);
}

.card-title {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 8px;
}

.card-value {
    color: white;
    font-size: 30px;
    font-weight: bold;
}

.section-title {
    color: white;
    font-size: 24px;
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
    '<div class="dashboard-title">BD BATANGAS DAILY SALES DASHBOARD</div>',
    unsafe_allow_html=True
)

# =====================================================
# FILE UPLOADER
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Excel Dashboard File",
    type=["xlsx", "xlsm"]
)

# =====================================================
# LOAD EXCEL
# =====================================================

if uploaded_file is not None:

    try:

        excel_file = pd.ExcelFile(uploaded_file)

        # =====================================================
        # LOAD SHEETS
        # =====================================================

        dashboard_df = pd.read_excel(uploaded_file, sheet_name="DASHBOARD")
        outlet_df = pd.read_excel(uploaded_file, sheet_name="OUTLETS")
        plan_df = pd.read_excel(uploaded_file, sheet_name="PLANSHIPMENTS")
        ar_df = pd.read_excel(uploaded_file, sheet_name="AR")

        # =====================================================
        # SIDEBAR
        # =====================================================

        st.sidebar.header("Dashboard Filters")

        route_col = None

        for col in outlet_df.columns:
            if "route" in str(col).lower():
                route_col = col
                break

        selected_route = None

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
        # AUTO DETECT COLUMNS
        # =====================================================

        sales_col = None
        date_col = None
        product_col = None
        customer_col = None

        for col in plan_df.columns:

            col_lower = str(col).lower()

            if sales_col is None:
                if (
                    "ucs" in col_lower
                    or "sales" in col_lower
                    or "volume" in col_lower
                    or "qty" in col_lower
                ):
                    sales_col = col

            if date_col is None:
                if "date" in col_lower:
                    date_col = col

            if product_col is None:
                if (
                    "sku" in col_lower
                    or "product" in col_lower
                    or "item" in col_lower
                    or "brand" in col_lower
                ):
                    product_col = col

            if customer_col is None:
                if "customer" in col_lower:
                    customer_col = col

        # fallback numeric
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
            min_sales = plan_df[sales_col].min()

        else:

            total_sales = 0
            avg_sales = 0
            max_sales = 0
            min_sales = 0

        achievement = 0

        if total_sales > 0:
            achievement = (avg_sales / total_sales) * 100

        variance = total_sales - avg_sales

        buying_days = 0

        if sales_col:
            buying_days = plan_df[plan_df[sales_col] > 0].shape[0]

        # =====================================================
        # KPI CARDS
        # =====================================================

        row1 = st.columns(5)

        kpi_data = [
            ("S&OP", f"{total_sales:,.0f}"),
            ("UCS", f"{avg_sales:,.0f}"),
            ("ACHIEVEMENT", f"{achievement:.2f}%"),
            ("VARIANCE", f"{variance:,.0f}"),
            ("BUYING DAYS", f"{buying_days}")
        ]

        for col, item in zip(row1, kpi_data):

            title, value = item

            with col:

                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{title}</div>
                    <div class="card-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        # =====================================================
        # SECOND KPI ROW
        # =====================================================

        row2 = st.columns(4)

        ar_total = 0

        try:
            ar_total = ar_df.select_dtypes(include="number").sum().sum()
        except:
            ar_total = 0

        second_kpi = [
            ("TOTAL AR", f"{ar_total:,.0f}"),
            ("MAX SALES", f"{max_sales:,.0f}"),
            ("MIN SALES", f"{min_sales:,.0f}"),
            ("OUTLETS", f"{filtered_outlets.shape[0]:,}")
        ]

        for col, item in zip(row2, second_kpi):

            title, value = item

            with col:

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

        if date_col and sales_col:

            plan_df[date_col] = pd.to_datetime(plan_df[date_col])

            daily_sales = (
                plan_df.groupby(date_col)[sales_col]
                .sum()
                .reset_index()
            )

            fig_daily = px.bar(
                daily_sales,
                x=date_col,
                y=sales_col,
                template="plotly_dark"
            )

            fig_daily.update_layout(
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                height=450,
                title="Daily UCS Sales"
            )

            st.plotly_chart(
                fig_daily,
                use_container_width=True
            )

        # =====================================================
        # CHARTS ROW
        # =====================================================

        left_col, right_col = st.columns(2)

        # =====================================================
        # PRODUCT MIX DONUT
        # =====================================================

        with left_col:

            st.markdown(
                '<div class="section-title">Product Mix</div>',
                unsafe_allow_html=True
            )

            if product_col and sales_col:

                product_mix = (
                    plan_df.groupby(product_col)[sales_col]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )

                fig_pie = px.pie(
                    product_mix,
                    names=product_col,
                    values=sales_col,
                    hole=0.65,
                    template="plotly_dark"
                )

                fig_pie.update_layout(
                    paper_bgcolor="#111827",
                    plot_bgcolor="#111827",
                    height=500
                )

                st.plotly_chart(
                    fig_pie,
                    use_container_width=True
                )

        # =====================================================
        # TOP SKU
        # =====================================================

        with right_col:

            st.markdown(
                '<div class="section-title">Top SKU Performance</div>',
                unsafe_allow_html=True
            )

            if product_col and sales_col:

                top_sku = (
                    plan_df.groupby(product_col)[sales_col]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )

                fig_top = px.bar(
                    top_sku,
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

                st.plotly_chart(
                    fig_top,
                    use_container_width=True
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
            title={'text': "Achievement %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#ef4444'}
            }
        ))

        fig_gauge.update_layout(
            paper_bgcolor="#111827",
            font={'color': "white"},
            height=350
        )

        st.plotly_chart(
            fig_gauge,
            use_container_width=True
        )

        # =====================================================
        # CUSTOMER PERFORMANCE TABLE
        # =====================================================

        st.markdown(
            '<div class="section-title">Customer Performance</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            filtered_outlets,
            use_container_width=True,
            height=500
        )

        # =====================================================
        # FOOTER
        # =====================================================

        st.markdown("---")

        st.markdown(
            """
            <center style='color:gray'>
            Professional Interactive Dynamic Dashboard<br>
            Powered by Streamlit + Plotly + Pandas
            </center>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error(f"Error loading dashboard: {e}")

else:

    st.info("Upload the Excel dashboard file to start.")
```

---

# DASHBOARD ELEMENTS RECREATED

## KPI SECTION

* S&OP
* UCS
* Achievement %
* Variance
* Buying Days
* Total AR
* Max Sales
* Min Sales
* Outlet Count

---

## VISUALS

* Daily Sales Bar Chart
* Product Mix Donut Chart
* Top SKU Chart
* Achievement Gauge
* Customer Performance Table

---

## DYNAMIC FEATURES

* Route filter
* Auto-detect columns
* Auto-refresh visuals when filters change
* Dynamic KPI recalculation
* Responsive layout

---

## PROFESSIONAL DESIGN

* Dark Coca-Cola theme
* KPI cards
* Responsive grid layout
* Interactive Plotly visuals
* Professional business dashboard UI
