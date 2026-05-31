# Dynamic Sales Dashboard – Python Script

## Overview

This Python script analyzes the uploaded Excel workbook:

`P5 Dynamic Dashboard Batangas BD(2).xlsm`

It creates a professional interactive dashboard using:

* pandas
* plotly
* dash
* openpyxl

The dashboard includes:

* KPI Cards
* Route Analysis
* Outlet Performance
* Top Customers
* Achievement Monitoring
* Dynamic Charts
* Interactive Filters
* Auto-refresh ready structure

---

# FINAL CLEAN PYTHON CODE

```python
# ============================================================
# BD BATANGAS DYNAMIC SALES DASHBOARD
# ============================================================
# Author : ChatGPT
# Purpose: Interactive Dynamic Dashboard from Excel Workbook
# ============================================================

import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from dash.dash_table import DataTable
from pathlib import Path

# ============================================================
# FILE PATH
# ============================================================

FILE_PATH = r"P5 Dynamic Dashboard Batangas BD(2).xlsm"

# ============================================================
# LOAD EXCEL FILE
# ============================================================

excel_file = pd.ExcelFile(FILE_PATH)

# ============================================================
# LOAD SHEETS
# ============================================================

outlets_raw = pd.read_excel(FILE_PATH, sheet_name='OUTLETS')
bar_chart_df = pd.read_excel(FILE_PATH, sheet_name='BAR CHART')
pie_df = pd.read_excel(FILE_PATH, sheet_name='Dynamic PIE')
dashboard_df = pd.read_excel(FILE_PATH, sheet_name='DASHBOARD')

# ============================================================
# CLEAN OUTLETS DATA
# ============================================================

# Extract actual headers from row 1
outlets_headers = outlets_raw.iloc[1]
outlets = outlets_raw[2:].copy()
outlets.columns = outlets_headers

# Remove empty rows
outlets = outlets.dropna(subset=['Customer Name'])

# Reset index
outlets.reset_index(drop=True, inplace=True)

# ============================================================
# RENAME COLUMNS
# ============================================================

outlets.rename(columns={
    'Customer Name': 'Customer_Name',
    'Customer No': 'Customer_No',
    'PARTNER SUB MODEL': 'Partner_Model',
    'ACTUAL_UCS': 'Actual_UCS',
    'LY_UCS': 'LY_UCS',
    'S&OP_UCS': 'SOP_UCS',
    'VAR_vs_LY': 'VAR_vs_LY',
    'VAR_vs_S&OP': 'VAR_vs_SOP',
    'ACH_vs_LY': 'ACH_vs_LY',
    'ACH_vs_S&OP': 'ACH_vs_SOP'
}, inplace=True)

# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    'Actual_UCS',
    'LY_UCS',
    'SOP_UCS',
    'VAR_vs_LY',
    'VAR_vs_SOP',
    'ACH_vs_LY',
    'ACH_vs_SOP'
]

for col in numeric_columns:
    outlets[col] = pd.to_numeric(outlets[col], errors='coerce').fillna(0)

# ============================================================
# KPI CALCULATIONS
# ============================================================

TOTAL_ACTUAL = outlets['Actual_UCS'].sum()
TOTAL_TARGET = outlets['SOP_UCS'].sum()
TOTAL_LY = outlets['LY_UCS'].sum()

VARIANCE = TOTAL_ACTUAL - TOTAL_TARGET

if TOTAL_TARGET != 0:
    ACHIEVEMENT = (TOTAL_ACTUAL / TOTAL_TARGET) * 100
else:
    ACHIEVEMENT = 0

if TOTAL_LY != 0:
    GROWTH = ((TOTAL_ACTUAL - TOTAL_LY) / TOTAL_LY) * 100
else:
    GROWTH = 0

TOTAL_OUTLETS = outlets['Customer_Name'].nunique()
TOTAL_ROUTES = outlets['ROUTE'].nunique()

# ============================================================
# TOP CUSTOMERS
# ============================================================

TOP_CUSTOMERS = (
    outlets.groupby('Customer_Name')['Actual_UCS']
    .sum()
    .reset_index()
    .sort_values(by='Actual_UCS', ascending=False)
    .head(10)
)

# ============================================================
# ROUTE PERFORMANCE
# ============================================================

ROUTE_PERFORMANCE = (
    outlets.groupby('ROUTE')[['Actual_UCS', 'SOP_UCS', 'LY_UCS']]
    .sum()
    .reset_index()
)

# ============================================================
# DASH APPLICATION
# ============================================================

app = Dash(__name__)

# ============================================================
# LAYOUT
# ============================================================

app.layout = html.Div([

    # ========================================================
    # HEADER
    # ========================================================

    html.Div([
        html.H1(
            "BD BATANGAS SALES DASHBOARD",
            style={
                'textAlign': 'center',
                'color': 'white',
                'padding': '15px'
            }
        )
    ], style={
        'backgroundColor': '#d62828',
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),

    # ========================================================
    # FILTERS
    # ========================================================

    html.Div([

        html.Div([
            html.Label('Select Route'),
            dcc.Dropdown(
                id='route_filter',
                options=[
                    {'label': r, 'value': r}
                    for r in sorted(outlets['ROUTE'].dropna().unique())
                ],
                multi=True,
                placeholder='Select Route'
            )
        ], style={'width': '30%'}),

    ], style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '20px'
    }),

    # ========================================================
    # KPI CARDS
    # ========================================================

    html.Div([

        html.Div([
            html.H3('TOTAL SALES'),
            html.H2(f"{TOTAL_ACTUAL:,.2f}")
        ], className='card'),

        html.Div([
            html.H3('TARGET'),
            html.H2(f"{TOTAL_TARGET:,.2f}")
        ], className='card'),

        html.Div([
            html.H3('ACHIEVEMENT %'),
            html.H2(f"{ACHIEVEMENT:.2f}%")
        ], className='card'),

        html.Div([
            html.H3('VS LAST YEAR'),
            html.H2(f"{GROWTH:.2f}%")
        ], className='card'),

        html.Div([
            html.H3('TOTAL OUTLETS'),
            html.H2(f"{TOTAL_OUTLETS:,.0f}")
        ], className='card'),

        html.Div([
            html.H3('TOTAL ROUTES'),
            html.H2(f"{TOTAL_ROUTES:,.0f}")
        ], className='card'),

    ], style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(6, 1fr)',
        'gap': '15px',
        'marginBottom': '25px'
    }),

    # ========================================================
    # CHARTS ROW 1
    # ========================================================

    html.Div([

        dcc.Graph(id='route_chart', style={'width': '50%'}),
        dcc.Graph(id='top_customer_chart', style={'width': '50%'})

    ], style={'display': 'flex'}),

    # ========================================================
    # CHARTS ROW 2
    # ========================================================

    html.Div([

        dcc.Graph(id='achievement_gauge', style={'width': '50%'}),
        dcc.Graph(id='pie_chart', style={'width': '50%'})

    ], style={'display': 'flex'}),

    # ========================================================
    # DATA TABLE
    # ========================================================

    html.Div([

        html.H2('Outlet Performance Table'),

        DataTable(
            id='table',
            columns=[
                {'name': i, 'id': i}
                for i in outlets.columns
            ],
            data=outlets.to_dict('records'),
            page_size=15,
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': '#d62828',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontSize': '12px'
            }
        )

    ])

], style={
    'padding': '20px',
    'fontFamily': 'Arial',
    'backgroundColor': '#f4f4f4'
})

# ============================================================
# CALLBACKS
# ============================================================

@app.callback(
    [
        Output('route_chart', 'figure'),
        Output('top_customer_chart', 'figure'),
        Output('achievement_gauge', 'figure'),
        Output('pie_chart', 'figure'),
        Output('table', 'data')
    ],
    [
        Input('route_filter', 'value')
    ]
)
def update_dashboard(selected_routes):

    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered_df = outlets.copy()

    if selected_routes and len(selected_routes) > 0:
        filtered_df = filtered_df[
            filtered_df['ROUTE'].isin(selected_routes)
        ]

    # ========================================================
    # ROUTE CHART
    # ========================================================

    route_summary = (
        filtered_df.groupby('ROUTE')[['Actual_UCS', 'SOP_UCS']]
        .sum()
        .reset_index()
    )

    route_fig = px.bar(
        route_summary,
        x='ROUTE',
        y=['Actual_UCS', 'SOP_UCS'],
        barmode='group',
        title='Route Performance'
    )

    # ========================================================
    # TOP CUSTOMER CHART
    # ========================================================

    top_customer = (
        filtered_df.groupby('Customer_Name')['Actual_UCS']
        .sum()
        .reset_index()
        .sort_values(by='Actual_UCS', ascending=False)
        .head(10)
    )

    customer_fig = px.bar(
        top_customer,
        x='Actual_UCS',
        y='Customer_Name',
        orientation='h',
        title='Top 10 Customers'
    )

    # ========================================================
    # ACHIEVEMENT GAUGE
    # ========================================================

    actual = filtered_df['Actual_UCS'].sum()
    target = filtered_df['SOP_UCS'].sum()

    if target != 0:
        achievement = (actual / target) * 100
    else:
        achievement = 0

    gauge_fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=achievement,
        title={'text': 'Achievement %'},
        gauge={
            'axis': {'range': [0, 150]},
            'bar': {'color': 'green'},
            'steps': [
                {'range': [0, 70], 'color': 'lightgray'},
                {'range': [70, 100], 'color': 'yellow'},
                {'range': [100, 150], 'color': 'lightgreen'}
            ]
        }
    ))

    # ========================================================
    # PIE CHART
    # ========================================================

    pie_data = pd.DataFrame({
        'Category': ['Actual', 'Remaining'],
        'Value': [actual, max(target - actual, 0)]
    })

    pie_fig = px.pie(
        pie_data,
        names='Category',
        values='Value',
        title='Target Achievement Distribution'
    )

    # ========================================================
    # RETURN OUTPUTS
    # ========================================================

    return (
        route_fig,
        customer_fig,
        gauge_fig,
        pie_fig,
        filtered_df.to_dict('records')
    )

# ============================================================
# CUSTOM CSS
# ============================================================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>BD Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f4f4f4;
            }

            .card {
                background-color: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                text-align: center;
            }

            .card h3 {
                color: gray;
                font-size: 14px;
            }

            .card h2 {
                color: #d
```
