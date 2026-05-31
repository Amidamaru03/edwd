# ============================================================
# BD BATANGAS DYNAMIC SALES DASHBOARD
# FINAL CLEAN VERSION - FIXED
# ============================================================

import pandas as pd
import numpy as np

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.dash_table import DataTable

import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# FILE PATH
# ============================================================

FILE_PATH = "P5 Dynamic Dashboard Batangas BD(2).xlsm"

# ============================================================
# LOAD EXCEL FILE
# ============================================================

outlets_raw = pd.read_excel(FILE_PATH, sheet_name="OUTLETS")

# ============================================================
# CLEAN DATA
# ============================================================

# Get correct headers
headers = outlets_raw.iloc[1]

# Remove top rows
df = outlets_raw.iloc[2:].copy()

# Apply headers
df.columns = headers

# Remove empty rows
df = df.dropna(subset=["Customer Name"])

# Reset index
df.reset_index(drop=True, inplace=True)

# ============================================================
# RENAME COLUMNS
# ============================================================

df.rename(columns={
    "Customer Name": "Customer_Name",
    "Customer No": "Customer_No",
    "PARTNER SUB MODEL": "Partner_Model",
    "ACTUAL_UCS": "Actual_UCS",
    "LY_UCS": "LY_UCS",
    "S&OP_UCS": "SOP_UCS",
    "VAR_vs_LY": "VAR_vs_LY",
    "VAR_vs_S&OP": "VAR_vs_SOP",
    "ACH_vs_LY": "ACH_vs_LY",
    "ACH_vs_S&OP": "ACH_vs_SOP"
}, inplace=True)

# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_cols = [
    "Actual_UCS",
    "LY_UCS",
    "SOP_UCS",
    "VAR_vs_LY",
    "VAR_vs_SOP",
    "ACH_vs_LY",
    "ACH_vs_SOP"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ============================================================
# KPI CALCULATIONS
# ============================================================

TOTAL_ACTUAL = df["Actual_UCS"].sum()
TOTAL_TARGET = df["SOP_UCS"].sum()
TOTAL_LY = df["LY_UCS"].sum()

ACHIEVEMENT = (
    (TOTAL_ACTUAL / TOTAL_TARGET) * 100
    if TOTAL_TARGET != 0 else 0
)

GROWTH = (
    ((TOTAL_ACTUAL - TOTAL_LY) / TOTAL_LY) * 100
    if TOTAL_LY != 0 else 0
)

TOTAL_OUTLETS = df["Customer_Name"].nunique()

TOTAL_ROUTES = (
    df["ROUTE"].nunique()
    if "ROUTE" in df.columns else 0
)

# ============================================================
# CREATE DASH APP
# ============================================================

app = Dash(__name__)

# ============================================================
# APP LAYOUT
# ============================================================

app.layout = html.Div([

    # ========================================================
    # HEADER
    # ========================================================

    html.Div([
        html.H1(
            "BD BATANGAS SALES DASHBOARD",
            style={
                "textAlign": "center",
                "color": "white",
                "padding": "20px"
            }
        )
    ], style={
        "backgroundColor": "#d62828",
        "borderRadius": "10px",
        "marginBottom": "20px"
    }),

    # ========================================================
    # FILTER
    # ========================================================

    html.Div([

        html.Label("Select Route"),

        dcc.Dropdown(
            id="route_filter",

            options=[
                {"label": r, "value": r}
                for r in sorted(df["ROUTE"].dropna().unique())
            ] if "ROUTE" in df.columns else [],

            multi=True,
            placeholder="Select Route"
        )

    ], style={
        "marginBottom": "20px"
    }),

    # ========================================================
    # KPI CARDS
    # ========================================================

    html.Div([

        html.Div([
            html.H3("TOTAL SALES"),
            html.H2(f"{TOTAL_ACTUAL:,.2f}")
        ], className="card"),

        html.Div([
            html.H3("TARGET"),
            html.H2(f"{TOTAL_TARGET:,.2f}")
        ], className="card"),

        html.Div([
            html.H3("ACHIEVEMENT %"),
            html.H2(f"{ACHIEVEMENT:.2f}%")
        ], className="card"),

        html.Div([
            html.H3("VS LAST YEAR"),
            html.H2(f"{GROWTH:.2f}%")
        ], className="card"),

        html.Div([
            html.H3("TOTAL OUTLETS"),
            html.H2(f"{TOTAL_OUTLETS}")
        ], className="card"),

        html.Div([
            html.H3("TOTAL ROUTES"),
            html.H2(f"{TOTAL_ROUTES}")
        ], className="card")

    ], style={
        "display": "grid",
        "gridTemplateColumns": "repeat(6, 1fr)",
        "gap": "15px",
        "marginBottom": "25px"
    }),

    # ========================================================
    # CHARTS
    # ========================================================

    html.Div([

        dcc.Graph(id="route_chart"),

        dcc.Graph(id="top_customer_chart"),

        dcc.Graph(id="achievement_gauge"),

        dcc.Graph(id="pie_chart")

    ]),

    # ========================================================
    # TABLE
    # ========================================================

    html.H2("Outlet Performance"),

    DataTable(
        id="table",

        columns=[
            {"name": i, "id": i}
            for i in df.columns
        ],

        data=df.to_dict("records"),

        page_size=15,

        style_table={
            "overflowX": "auto"
        },

        style_header={
            "backgroundColor": "#d62828",
            "color": "white",
            "fontWeight": "bold"
        },

        style_cell={
            "padding": "8px",
            "textAlign": "left",
            "fontSize": "12px"
        }
    )

], style={
    "padding": "20px",
    "fontFamily": "Arial",
    "backgroundColor": "#f5f5f5"
})

# ============================================================
# CALLBACKS
# ============================================================

@app.callback(

    [
        Output("route_chart", "figure"),
        Output("top_customer_chart", "figure"),
        Output("achievement_gauge", "figure"),
        Output("pie_chart", "figure"),
        Output("table", "data")
    ],

    [
        Input("route_filter", "value")
    ]
)

def update_dashboard(selected_routes):

    filtered_df = df.copy()

    # ========================================================
    # FILTERING
    # ========================================================

    if (
        selected_routes
        and "ROUTE" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["ROUTE"].isin(selected_routes)
        ]

    # ========================================================
    # ROUTE PERFORMANCE
    # ========================================================

    if "ROUTE" in filtered_df.columns:

        route_summary = (
            filtered_df.groupby("ROUTE")[[
                "Actual_UCS",
                "SOP_UCS"
            ]]
            .sum()
            .reset_index()
        )

        route_fig = px.bar(
            route_summary,
            x="ROUTE",
            y=["Actual_UCS", "SOP_UCS"],
            barmode="group",
            title="Route Performance"
        )

    else:

        route_fig = go.Figure()

    # ========================================================
    # TOP CUSTOMERS
    # ========================================================

    top_customer = (
        filtered_df.groupby("Customer_Name")["Actual_UCS"]
        .sum()
        .reset_index()
        .sort_values(by="Actual_UCS", ascending=False)
        .head(10)
    )

    customer_fig = px.bar(
        top_customer,
        x="Actual_UCS",
        y="Customer_Name",
        orientation="h",
        title="Top 10 Customers"
    )

    # ========================================================
    # ACHIEVEMENT GAUGE
    # ========================================================

    actual = filtered_df["Actual_UCS"].sum()
    target = filtered_df["SOP_UCS"].sum()

    achievement = (
        (actual / target) * 100
        if target != 0 else 0
    )

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=achievement,

        title={
            "text": "Achievement %"
        },

        gauge={
            "axis": {
                "range": [0, 150]
            },

            "steps": [
                {
                    "range": [0, 70],
                    "color": "lightgray"
                },
                {
                    "range": [70, 100],
                    "color": "yellow"
                },
                {
                    "range": [100, 150],
                    "color": "lightgreen"
                }
            ]
        }
    ))

    # ========================================================
    # PIE CHART
    # ========================================================

    pie_data = pd.DataFrame({
        "Category": ["Actual", "Remaining"],
        "Value": [
            actual,
            max(target - actual, 0)
        ]
    })

    pie_fig = px.pie(
        pie_data,
        names="Category",
        values="Value",
        title="Target Achievement Distribution"
    )

    # ========================================================
    # RETURN
    # ========================================================

    return (
        route_fig,
        customer_fig,
        gauge_fig,
        pie_fig,
        filtered_df.to_dict("records")
    )

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050
    )
