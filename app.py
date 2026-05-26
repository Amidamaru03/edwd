import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="LIVE Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================
# MOBILE / TABLET RESPONSIVE DESIGN
# =========================================

st.markdown("""
<style>

/* GLOBAL */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* KPI CARDS */
[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #374151;
    padding: 15px;
    border-radius: 16px;
    text-align: center;
}

/* TABLE */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* FONT */
html, body, [class*="css"] {
    font-size: 14px;
}

/* MOBILE */
@media (max-width: 768px) {

    .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }

    h1 {
        font-size: 28px !important;
        text-align: center;
    }

    h2, h3 {
        font-size: 18px !important;
    }

    [data-testid="metric-container"] {
        padding: 10px;
    }
}

/* TABLET */
@media (min-width: 769px) and (max-width: 1024px) {

    h1 {
        font-size: 34px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================

st.title("🚀 LIVE Sales Dashboard")
st.markdown("Upload updated Excel files and refresh analytics instantly.")

# =========================================
# FILE UPLOADER
# =========================================

uploaded_file = st.file_uploader(
    "📂 Upload Excel File",
    type=["xlsx", "xls"]
)

# =========================================
# MAIN DASHBOARD
# =========================================

if uploaded_file:

    # READ EXCEL
    df = pd.read_excel(uploaded_file, header=6)

    # REMOVE EMPTY ROWS/COLUMNS
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.isna()]

    # CLEAN COLUMN NAMES
    df.columns = df.columns.astype(str).str.strip()

    # =========================================
    # FORMAT DATE COLUMNS
    # =========================================

    for col in df.columns:

        if 'date' in col.lower():

            try:
                df[col] = pd.to_datetime(df[col])

                df[col] = df[col].dt.strftime(
                    '%A, %m/%d/%Y'
                )

            except:
                pass

    # =========================================
    # NUMERIC COLUMNS
    # =========================================

    numeric_cols = [
        'S&OP',
        'SNOP',
        'TOTAL UCS',
        'ACV VS S7OP',
        'VARIANCE TO HIT'
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors='coerce'
            )

    # =========================================
    # PERCENTAGE FORMAT
    # =========================================

    if 'ACV VS S7OP' in df.columns:

        df['ACV VS S7OP'] = (
            df['ACV VS S7OP'] * 100
        )

    # =========================================
    # ROUND VALUES
    # =========================================

    for col in numeric_cols:

        if col in df.columns:

            df[col] = df[col].round(2)

    # =========================================
    # KPI CALCULATIONS
    # =========================================

    total_ucs = (
        df['TOTAL UCS'].sum()
        if 'TOTAL UCS' in df.columns
        else 0
    )

    total_snop = (
        df['SNOP'].sum()
        if 'SNOP' in df.columns
        else 0
    )

    total_variance = (
        df['VARIANCE TO HIT'].sum()
        if 'VARIANCE TO HIT' in df.columns
        else 0
    )

    avg_acv = (
        df['ACV VS S7OP'].mean()
        if 'ACV VS S7OP' in df.columns
        else 0
    )

    # =========================================
    # KPI DISPLAY
    # =========================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total UCS",
        f"{total_ucs:,.2f}"
    )

    col2.metric(
        "Total SNOP",
        f"{total_snop:,.2f}"
    )

    col3.metric(
        "Total Variance",
        f"{total_variance:,.2f}"
    )

    col4.metric(
        "Average ACV VS S7OP",
        f"{avg_acv:,.2f}%"
    )

    st.divider()

    # =========================================
    # CHARTS
    # =========================================

    chart_col1, chart_col2 = st.columns(2)

    # TOP CUSTOMERS
    if (
        'Customer Name' in df.columns
        and 'TOTAL UCS' in df.columns
    ):

        top_customers = (
            df.groupby('Customer Name')['TOTAL UCS']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig1 = px.bar(
            top_customers,
            x='Customer Name',
            y='TOTAL UCS',
            title='Top 10 Customers by TOTAL UCS'
        )

        chart_col1.plotly_chart(
            fig1,
            use_container_width=True
        )

    # PARTNER MODEL
    if (
        'PARTNER SUB MODEL' in df.columns
        and 'TOTAL UCS' in df.columns
    ):

        partner_data = (
            df.groupby('PARTNER SUB MODEL')['TOTAL UCS']
            .sum()
            .reset_index()
        )

        fig2 = px.pie(
            partner_data,
            names='PARTNER SUB MODEL',
            values='TOTAL UCS',
            title='Partner Sub Model Distribution'
        )

        chart_col2.plotly_chart(
            fig2,
            use_container_width=True
        )

    # ROUTE TREND
    if (
        'ROUTE' in df.columns
        and 'TOTAL UCS' in df.columns
    ):

        route_data = (
            df.groupby('ROUTE')['TOTAL UCS']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig3 = px.line(
            route_data,
            x='ROUTE',
            y='TOTAL UCS',
            title='Top Routes by TOTAL UCS'
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    st.divider()

    # =========================================
    # SEARCHABLE TABLE
    # =========================================

    st.subheader("📋 Detailed Data")

    search = st.text_input(
        "🔍 Search Entire Table"
    )

    filtered_df = df.copy()

    if search:

        mask = filtered_df.astype(str).apply(
            lambda x: x.str.contains(
                search,
                case=False,
                na=False
            )
        ).any(axis=1)

        filtered_df = filtered_df[mask]

    # =========================================
    # FORMAT DISPLAY TABLE
    # =========================================

    display_df = filtered_df.copy()

    for col in numeric_cols:

        if col in display_df.columns:

            display_df[col] = display_df[col].map(
                lambda x:
                f"{x:,.2f}"
                if pd.notnull(x)
                else ""
            )

    if 'ACV VS S7OP' in display_df.columns:

        display_df['ACV VS S7OP'] = (
            display_df['ACV VS S7OP']
            .astype(str)
            .replace('nan', '')
            + '%'
        )

    # =========================================
    # SHOW TABLE
    # =========================================

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500
    )

    # =========================================
    # DOWNLOAD CSV
    # =========================================

    csv = filtered_df.to_csv(
        index=False
    ).encode('utf-8')

    st.download_button(
        label='⬇ Download CSV',
        data=csv,
        file_name='sales_dashboard_export.csv',
        mime='text/csv'
    )

else:

    st.info(
        "Upload an Excel file to start the dashboard."
    )