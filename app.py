# --- Cleaned Dash App for Tapix AI Finance Assistant ---
import os
from pathlib import Path
from datetime import datetime
import calendar
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, callback_context, MATCH, ALL
from dash_echarts import DashECharts
import dash_bootstrap_components as dbc
# from backend import generate_ai_response  # Uncomment if backend.py exists
import random

# 1. Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 2. Load your data
try:
    df = pd.read_csv('Tapix enriched data sample')
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        'date', 'amount', 'category', 'merchant', 'currency', 'tags',
        'merchant_logo', 'category_logo', 'address', 'lat', 'long',
        'co2FootprintValue', 'co2FootprintUnit', 'url'
    ])
    df['month'] = pd.Series(dtype='str')

# 3. Define variables before layout
if not df.empty:
    default_month = df['month'].max()
else:
    default_month = "2024-01"

month_options = [
    {"label": "January 2024", "value": "2024-01"},
    {"label": "February 2024", "value": "2024-02"},
    # Add more months as needed
]

initial_chat = [
    {"role": "assistant", "content": "Hello! I'm your AI finance assistant. How can I help you analyze your spending today?"}
]

suggested_questions = [
    "What did I spend the most on this month?",
    "Show me my largest transactions",
    "How does this month compare to last month?",
    "What categories should I focus on reducing?"
]

# 4. (Optional) Reminder for CSS
# Make sure you have your glassmorphism styles in assets/styles.css

from dash import html
# Add a dcc.Store to track dropdown open/close and selected value
_layout = html.Div([
    html.Div([
        html.Div(className="orb orb-1"),
        html.Div(className="orb orb-2"),
        html.Div(className="orb orb-3"),
    ], className="glass-background", **{"aria-hidden": "true"}),
    dcc.Store(id="month-dropdown-store", data={"open": False, "value": default_month}),
    dcc.Store(id="theme-store", data="light"),
    dcc.Store(id="selected-transaction"),
    html.Div([
        dbc.Container([
            dbc.Row([
                # Quick Snapshot Sidebar (left)
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.H3("Quick Snapshot", className="glass-metrics-heading", style={"fontSize": "2.5rem", "textAlign": "left", "margin": 0}),
                            html.Div([
                                html.Div([
                                    html.Span([
                                        next((o["label"] for o in month_options if o["value"] == default_month), default_month),
                                        html.Span(
                                            html.Span("", id="month-chevron", style={"display": "inline-block", "marginLeft": "0.7em", "transition": "transform 0.3s"}),
                                            style={"display": "inline-block", "verticalAlign": "middle"}
                                        )
                                    ], id="month-dropdown-selected", n_clicks=0, style={
                                        "background": "rgba(255,255,255,0.15)",
                                        "backdropFilter": "blur(10px)",
                                        "borderRadius": "16px",
                                        "padding": "16px 20px",
                                        "fontWeight": 500,
                                        "color": "#fff",
                                        "border": "1.5px solid rgba(255,255,255,0.2)",
                                        "boxShadow": "0 2px 8px rgba(56,217,150,0.10)",
                                        "cursor": "pointer",
                                        "outline": "none",
                                        "position": "relative",
                                        "width": "100%",
                                        "transition": "all 0.3s ease"
                                    }),
                                    html.Ul([
                                        html.Li(o["label"], id={"type": "month-dropdown-option", "value": o["value"]}, n_clicks=0, style={
                                            "padding": "12px 20px",
                                            "fontSize": "18px",
                                            "color": "#fff",
                                            "background": "rgba(40,60,90,0.85)",
                                            "borderBottom": "1px solid rgba(255,255,255,0.08)",
                                            "cursor": "pointer",
                                            "transition": "background 0.2s, color 0.2s",
                                            "fontWeight": 500
                                        }) for o in month_options
                                    ], id="month-dropdown-list", style={
                                        "position": "absolute",
                                        "top": "calc(100% + 6px)",
                                        "left": 0,
                                        "right": 0,
                                        "zIndex": 100,
                                        "background": "rgba(40,60,90,0.97)",
                                        "borderRadius": "16px",
                                        "boxShadow": "0 8px 32px rgba(56,217,150,0.10)",
                                        "border": "1.5px solid #a5d8ff",
                                        "overflowY": "auto",
                                        "maxHeight": "260px",
                                        "margin": 0,
                                        "padding": 0,
                                        "pointerEvents": "none",
                                        "transition": "opacity 0.3s, transform 0.3s",
                                        "transform": "translateY(-10px)"
                                    }, **{"data-simplebar": "true"})
                                ], style={"position": "relative", "width": "100%"})
                            ], id="month-dropdown-container", style={"width": "100%", "marginBottom": "0", "textAlign": "left", "paddingTop": 0})
                        ], style={"marginLeft": "auto"})
                        ], style={"display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "space-between", "marginBottom": "1.2em", "width": "100%"}),
                        html.Div([
                            html.Div(id="stats-block", style={"flex": "0 0 auto", "margin": 0, "padding": 0}),
                            html.Div([
                                # pie_chart reference removed from top-level layout
                            ], id="pie-block", style={
                                "width": "100%",
                                "height": "100%",
                                "minHeight": "320px",
                                "flex": 1,
                                "boxSizing": "border-box",
                                "display": "flex",
                                "flexDirection": "column",
                                "overflow": "visible",
                                "background": "rgba(30,41,59,0.95)",
                                "borderRadius": "1em",
                                "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                                "border": "1px solid rgba(56,217,150,0.2)"
                            }),
                        ], style={"display": "flex", "flexDirection": "column", "height": "100%", "flex": 1}),
                    ], className="glass-metrics", style={
                        "padding": "1em",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "flex-start",
                        "flex": 1,
                        "height": "100%",
                        "width": "100%",
                        "boxSizing": "border-box",
                        "marginBottom": 0
                    })
                ],
                style={
                    "background": "rgba(30,41,59,0.95)",
                    "borderRadius": "1em",
                    "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                    "flex": 1,
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "minWidth": "350px",
                    "padding": "2.5em 2em 2em 2em"
                }),
                # Chat container (middle)
                dbc.Col([
                    dcc.Store(id="chat-store", data=initial_chat),
                    dcc.Store(id="loading-store", data=False),
                    html.Div([
                        html.Div(id="chat-history", style={"padding": "2vw", "height": "60vh", "minHeight": "250px", "maxHeight": "70vh", "overflowY": "auto", "background": "transparent", "fontSize": "1.2em", "wordBreak": "break-word"}),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Textarea(id="chat-input", placeholder="Type your question and press Enter...", className="glass-input", style={"width": "100%", "height": "2.5em", "resize": "none", "minHeight": "2em", "maxHeight": "6em", "fontSize": "1.1em", "padding": "0.5em"}, title="Chat input"),
                                ], width=9),
                                dbc.Col([
                                    dbc.Button([
                                        html.Span("✈️", className="send-icon", style={"marginRight": "0.5em", "fontSize": "1.2em"}),
                                        "Send"
                                    ], id="send-btn", color="primary", n_clicks=0, className="glass-button", style={"width": "100%", "height": "2.5em", "minHeight": "2em", "maxHeight": "6em", "fontSize": "1.1em", "padding": "0.5em"}, title="Send message")
                                ], width=3)
                            ], style={"margin": "0 2rem 2rem 2rem"}),
                            html.Div([
                                dbc.Button(q, id={"type": "suggested-btn", "index": i}, n_clicks=0, className="glass-button glass-pill suggested-btn", style={"marginRight": "0.5rem", "marginBottom": "0.5rem", "fontSize": "1.18em", "minWidth": "220px", "padding": "0.7em 1.2em", "whiteSpace": "normal", "wordBreak": "break-word"}, title=f"Suggested question: {q}")
                                for i, q in enumerate(suggested_questions)
                            ], className="suggested-btn-row", style={"margin": "0 2vw 1vw 2vw", "display": "flex", "flexWrap": "wrap"}),
                        ]),
                    ], className="glass-card", style={
                        "background": "rgba(30,41,59,0.95)",
                        "borderRadius": "1em",
                        "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                        "flex": 1,
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%"
                    })
                ],
                style={
                    "background": "rgba(30,41,59,0.95)",
                    "borderRadius": "1em",
                    "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                    "flex": 1,
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "minWidth": "350px",
                    "padding": "2.5em 2em 2em 2em"
                }),
                # Transaction history (right)
                dbc.Col([
                    html.Div([
                        html.H3("Transactions", className="glass-metrics-heading", style={"marginTop": "1.5rem", "fontSize": "2.5rem", "textAlign": "left", "paddingLeft": "1.2em"}),
                        html.Div(id="transaction-list-block", style={
                            "height": "100%",
                            "overflowY": "auto",
                            "display": "flex",
                            "flexDirection": "column"
                        }),
                    ], className="glass-metrics", style={
                        "background": "rgba(30,41,59,0.95)",
                        "borderRadius": "1em",
                        "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                        "flex": 1,
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "minWidth": "350px",
                        "padding": "2.5em 2em 2em 2em"
                    })
                ],
                style={
                    "background": "rgba(30,41,59,0.95)",
                    "borderRadius": "1em",
                    "boxShadow": "0 8px 32px rgba(0,0,0,0.4)",
                    "flex": 1,
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "minWidth": "350px",
                    "padding": "2.5em 2em 2em 2em"
                })
            ], style={
                "height": "90vh",
                "display": "flex",
                "alignItems": "stretch",
                "gap": "3vw",
                "padding": "2vw 0",
                "maxWidth": "1600px",
                "margin": "0 auto"
            }),
            # Transaction Details Modal (hidden by default)
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Transaction Details"), close_button=True),
                dbc.ModalBody(id="transaction-details-body"),
            ], id="transaction-details-modal", is_open=False, size="xl", centered=True, backdrop=True),
        ])
    ], id="theme-content")

app.layout = _layout

# Sidebar callbacks for stats and pie chart
@app.callback(
    Output("stats-block", "children"),
    Output("pie-block", "children"),
    Output("transaction-list-block", "children"),
    Input("month-dropdown-store", "data")
)
def update_sidebar(month_store):
    selected_month = month_store.get("value") if month_store else None
    if not selected_month or df.empty:
        return [html.P("No data available.")], [], []
    # Use string comparison for month to match dropdown value
    month_df = df[df["month"].astype(str) == selected_month]
    month_total = month_df["amount"].sum()
    top_cat = month_df.groupby("category")["amount"].sum().sort_values(ascending=False).head(1)
    top_cat_name = str(top_cat.index[0]) if not top_cat.empty else "–"
    # Localized currency formatting for sidebar
    sidebar_currency = month_df["currency"].iloc[0] if not month_df.empty else "USD"
    currency_symbols = {
        "GBP": "£", "EUR": "€", "USD": "$", "CZK": "Kč", "PLN": "zł", "HUF": "Ft", "RON": "lei", "AUD": "$", "CAD": "$", "CHF": "Fr.", "SEK": "kr", "NOK": "kr", "DKK": "kr", "JPY": "¥", "CNY": "¥", "SGD": "$", "INR": "₹"
    }
    symbol = currency_symbols.get(sidebar_currency, sidebar_currency)
    try:
        sidebar_amount_str = f"{float(month_total):,.2f}"
    except Exception:
        sidebar_amount_str = str(month_total)
    if symbol in ["£", "€", "$", "¥", "₹"]:
        sidebar_display_amount = f"{symbol}{sidebar_amount_str}"
    elif symbol in ["Kč", "zł", "Ft", "lei", "Fr.", "kr"]:
        sidebar_display_amount = f"{sidebar_amount_str} {symbol}"
    else:
        sidebar_display_amount = f"{sidebar_amount_str} {symbol}"
    stats = [
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("\ud83d\udcb8", className="sidebar-stat-icon", style={"fontSize": "2em", "marginRight": "0.5em"}),
                html.Span("This Month's Spend", style={"fontWeight": 700, "fontSize": "1.3em", "color": "#fff"}),
            ], style={"display": "flex", "alignItems": "center"}), width=7, style={"display": "flex", "alignItems": "center"}),
            dbc.Col(html.Div([
                html.Span(f"{sidebar_amount_str}", style={"fontWeight": 900, "fontSize": "2em", "color": "#38d996", "textAlign": "right", "marginRight": "0.2em", "display": "inline-block"}),
                html.Span(symbol, style={"fontWeight": 900, "fontSize": "2em", "color": "#38d996", "textAlign": "right", "display": "inline-block"}),
            ], style={"textAlign": "right", "display": "flex", "alignItems": "center", "justifyContent": "flex-end"}), width=5, style={"display": "flex", "alignItems": "center", "justifyContent": "flex-end"})
        ], style={"marginBottom": "0.7em", "alignItems": "center"}),
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("🛒", className="sidebar-stat-icon", style={"fontSize": "2em", "marginRight": "0.5em"}),
                html.Span("Top Category", style={"fontWeight": 700, "fontSize": "1.3em", "color": "#fff"}),
            ], style={"display": "flex", "alignItems": "center"}), width=7),
            dbc.Col(html.Div([
                html.Span(top_cat_name, style={"fontWeight": 800, "fontSize": "1.5em", "color": "#a5d8ff", "textAlign": "right"}),
            ], style={"textAlign": "right"}), width=5)
        ], style={"marginBottom": "0.7em", "alignItems": "center"}),
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("📊", className="sidebar-stat-icon", style={"fontSize": "2em", "marginRight": "0.5em"}),
                html.Span("Transactions", style={"fontWeight": 700, "fontSize": "1.3em", "color": "#fff"}),
            ], style={"display": "flex", "alignItems": "center"}), width=7),
            dbc.Col(html.Div([
                html.Span(f"{len(month_df):,}", style={"fontWeight": 900, "fontSize": "2em", "color": "#ffd6a5", "textAlign": "right"}),
            ], style={"textAlign": "right"}), width=5)
        ], style={"marginBottom": "0.7em", "alignItems": "center"})
    ]
    # Pie chart data and config
    pastel_colors = [
        '#a5d8ff', '#b2f2bb', '#ffd6a5', '#ffadad', '#cdb4db', '#b5ead7', '#f3c4fb', '#fdffb6', '#bdb2ff', '#b0efeb'
    ]
    pie_chart = html.Div()
    legend_block = html.Div()
    if not month_df.empty:
        cat_summary = month_df.groupby("category")['amount'].sum().sort_values(ascending=False)
        pie_data = [
            {"value": float(v), "name": str(k)} for k, v in zip(cat_summary.index, cat_summary.values)
        ]
        total = sum([d["value"] for d in pie_data])
        pie_option = {
            "backgroundColor": "rgba(40,60,90,0.0)",
            "tooltip": {
                "trigger": "item",
                "backgroundColor": "rgba(30,41,59,0.98)",
                "borderColor": "rgba(56,217,150,0.2)",
                "borderWidth": 1,
                "borderRadius": 18,
                "textStyle": {
                    "color": "#fff",
                    "fontFamily": "Inter, Arial, sans-serif",
                    "fontSize": 18,
                    "fontWeight": 600
                },
                "formatter": (
                    '<div style="line-height:1.6; padding: 0.2em 0;">'
                    '<span style="font-weight:700; color:#fff; font-size:1.15em;">{b}</span><br>'
                    '<span style="font-weight:700; color:#38d996; font-size:1.2em;">£{c:.2f}</span><br>'
                    '<span style="font-size:1.05em; color:#a5d8ff; font-weight:500;">({d}% of total)</span>'
                    '</div>'
                )
            },
            "series": [{
                "name": "Categories",
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["50%", "50%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 12,
                    "borderColor": "rgba(255,255,255,0.15)",
                    "borderWidth": 2
                },
                "label": {"show": False},
                "emphasis": {"label": {"show": False}, "scale": True, "scaleSize": 5},
                "labelLine": {"show": False},
                "data": pie_data,
                "color": pastel_colors[:len(pie_data)]
            }],
            "animation": True,
            "animationType": "scale",
            "animationEasing": "elasticOut"
        }
        pie_chart = DashECharts(
            option=pie_option,
            style={
                "width": "100%",
                "height": "340px",
                "maxWidth": "100%",
                "minWidth": "0",
                "background": "transparent",
                "borderRadius": "0",
                "boxShadow": "none",
                "margin": "0",
                "border": "none"
            },
            id=f"echarts-pie-{selected_month}"
        )
        # Custom legend
        legend_items = []
        for i, d in enumerate(pie_data[:6]):
            percent = f"{round((d['value'] / total * 100) if total else 0):.0f}%"
            legend_items.append(html.Div([
                html.Span(style={
                    "display": "inline-block",
                    "width": "1.2em",
                    "height": "1.2em",
                    "borderRadius": "50%",
                    "background": pastel_colors[i % len(pastel_colors)],
                    "marginRight": "0.9em",
                    "verticalAlign": "middle"
                }),
                html.Span(str(d["name"]), style={
                    "verticalAlign": "middle",
                    "fontWeight": 700,
                    "fontSize": "1.18em",
                    "color": "#fff",
                    "fontFamily": "Inter, Arial, sans-serif",
                    "flex": 1
                }),
                html.Span(percent, style={
                    "color": "#a5d8ff",
                    "fontWeight": 700,
                    "fontSize": "1.13em",
                    "marginRight": "1.2em",
                    "fontFamily": "Inter, Arial, sans-serif"
                }),
                html.Span(f"£{d['value']:,.2f}", style={
                    "color": "#38d996",
                    "fontWeight": 700,
                    "fontSize": "1.13em",
                    "fontFamily": "Inter, Arial, sans-serif"
                })
            ], style={
                "marginBottom": "0.5em",
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "center",
                "width": "100%",
                "justifyContent": "space-between"
            }))
        legend_block = html.Div(legend_items, style={
            "maxWidth": "100%",
            "boxSizing": "border-box",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
            "minHeight": "120px",
            "padding": "0.7em 0.5em 0 0.5em",
            "background": "transparent",
            "borderRadius": "0",
            "overflow": "auto",
            "margin": "0",
            "boxShadow": "none",
            "border": "none"
        })
    # Wrap pie chart and legend in a single container for seamless look
    pie_block = html.Div([
        pie_chart,
        legend_block
    ], style={
        "width": "100%",
        "background": "rgba(30,41,59,0.95)",
        "borderRadius": "1em",
        "boxShadow": "none",
        "margin": "0 0 1.5em 0",
        "padding": "0.5em 0.5em 0 0.5em",
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "stretch",
        "justifyContent": "flex-start",
        "border": "none"
    })
    # Transaction list (scrollable, show 5 at a time)
    tx_rows = []
    for idx, (_, row) in enumerate(month_df.reset_index(drop=True).iterrows()):
        # Format tags as a clean, comma-separated list
        tags = str(row['tags'])
        tags = tags.strip('{}[]')
        tags = tags.replace('"', '').replace("'", "")
        tags = ', '.join([t.strip() for t in tags.split(',') if t.strip()])
        tx_rows.append(
            dbc.Button([
                html.Img(src=row["merchant_logo"], style={"height": "2em", "width": "2em", "objectFit": "contain", "marginRight": "1em", "verticalAlign": "middle", "borderRadius": "8px", "background": "#fff"}),
                html.Div([
                    html.Div(row['merchant'], style={"fontWeight": 600, "fontSize": "1.1em"}),
                    html.Div(f"{row['category']}", style={"fontSize": "1em", "color": "#a5d8ff"}),
                ], style={"flex": 2}),
                html.Div(f"{row['amount']} {row['currency']}", style={"flex": 1, "fontWeight": 500, "fontSize": "1.1em", "textAlign": "right", "marginRight": "1em"}),
                html.Div(tags, style={"flex": 2, "fontStyle": "italic", "color": "#b2f2bb", "fontSize": "1em", "textAlign": "right"})
            ],
            id={"type": "transaction-btn", "index": idx},
            n_clicks=0,
            className="transaction-row-btn",
            style={
                "display": "flex", "alignItems": "center", "marginBottom": "0.5em", "background": "rgba(255,255,255,0.07)", "borderRadius": "8px", "padding": "1em 2em", "gap": "1em", "borderBottom": "1px solid rgba(255,255,255,0.10)", "width": "100%", "textAlign": "left"
            })
        )
    # Get the formatted month label for the selected month
    month_label = next((o["label"] for o in month_options if o["value"] == selected_month), selected_month)
    tx_list = html.Div([
        html.H5(month_label, style={"margin": "0.7em 0 0.3em 0", "color": "#fff", "fontSize": "1.3rem", "paddingLeft": "1.2em"}),
        html.Div(tx_rows, style={"height": "100%", "flex": 1, "padding": "0.5em"})
    ], style={"marginTop": "1em", "marginBottom": "1em", "height": "100%", "display": "flex", "flexDirection": "column", "flex": 1})
    return stats, pie_block, tx_list

# --- Step 1: Add user message and set loading to True immediately ---
@app.callback(
    [Output("chat-store", "data"), Output("loading-store", "data")],
    Input("send-btn", "n_clicks"),
    State("chat-input", "value"),
    State("chat-store", "data"),
    prevent_initial_call=True
)
def add_user_message(n_clicks, user_input, chat_history):
    if not user_input or not user_input.strip():
        return chat_history, False
    # Add user message
    chat_history = chat_history + [{"role": "user", "content": user_input}]
    return chat_history, True

# --- Step 2: When chat-store or loading-store changes, get AI response if loading is True ---
@app.callback(
    [Output("chat-store", "data", allow_duplicate=True), Output("loading-store", "data", allow_duplicate=True)],
    [Input("chat-store", "data"), Input("loading-store", "data"), Input("month-dropdown-store", "data")],
    prevent_initial_call=True,
)
def get_ai_response(chat_history, loading, month_store):
    selected_month = month_store.get("value") if month_store else None
    ctx = callback_context
    # Only run if loading is True and last message is from user
    if not loading or not chat_history or chat_history[-1]["role"] != "user":
        raise dash.exceptions.PreventUpdate
    # Prepare extra context for AI: all transactions and summary by month/category
    extra_context = {}
    if not df.empty:
        # All transactions (as records, but limit to 500 for safety)
        extra_context["all_transactions"] = df.head(500).to_dict('records')
        # Summary by month and category
        month_cat_summary = (
            df.groupby([df["transactionTimestamp"].dt.to_period("M"), "category"])["amount"].sum()
            .unstack(fill_value=0)
            .astype(float)
            .round(2)
        )
        extra_context["month_category_summary"] = month_cat_summary.reset_index().astype(str).to_dict('records')
    # Also keep the old context for the selected month
    if selected_month and not df.empty:
        month_df = df[df["month"].astype(str) == selected_month]
        extra_context.update({
            "total_transactions": len(month_df),
            "date_range": f"{month_df['transactionTimestamp'].min().strftime('%Y-%m-%d')} to {month_df['transactionTimestamp'].max().strftime('%Y-%m-%d')}",
            "total_spent": f"${month_df['amount'].sum():,.2f}",
            "categories": month_df['category'].unique().tolist(),
            "recent_transactions": month_df.head(10).to_dict('records')
        })
    try:
        reply = generate_ai_response(chat_history, extra_context=extra_context)
    except Exception as e:
        reply = f"⚠️ Sorry, I couldn't reach the AI service right now. Error: {str(e)}"
    chat_history = chat_history + [{"role": "assistant", "content": reply}]
    return chat_history, False

@app.callback(
    Output("chat-history", "children"),
    [Input("chat-store", "data"), Input("loading-store", "data")]
)
def render_chat(chat_history, loading):
    bubbles = []
    for msg in chat_history:
        if msg["role"] == "user":
            bubble_cls = "chat-bubble glass-user fade-in"
            avatar = html.Div("🧑", className="chat-avatar")
        else:
            bubble_cls = "chat-bubble glass-assistant fade-in"
            avatar = html.Div("🤖", className="chat-avatar")
        bubbles.append(html.Div([
            avatar,
            html.Div(dcc.Markdown(msg["content"], dangerously_allow_html=True), className=bubble_cls)
        ], className="chat-row slide-up", style={"display": "flex", "alignItems": "flex-end", "marginBottom": "0.5rem"}))
    if loading:
        # Add animated loading bubble
        bubbles.append(html.Div([
            html.Div("🤖", className="chat-avatar"),
            html.Div([
                html.Span(".", className="dot dot1"),
                html.Span(".", className="dot dot2"),
                html.Span(".", className="dot dot3")
            ], className="chat-bubble glass-assistant loading-bubble fade-in")
        ], className="chat-row slide-up", style={"display": "flex", "alignItems": "flex-end", "marginBottom": "0.5rem"}))
    return bubbles

# Add callback for suggested question buttons
from dash.dependencies import ALL

@app.callback(
    Output("chat-input", "value"),
    [
        Input("send-btn", "n_clicks"),
        Input({"type": "suggested-btn", "index": ALL}, "n_clicks")
    ],
    [
        State("chat-input", "value"),
        State({"type": "suggested-btn", "index": ALL}, "children")
    ],
    prevent_initial_call=True
)
def update_chat_input(send_clicks, suggested_clicks, chat_value, suggested_children):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "send-btn":
        return ""
    else:
        # Find which suggested button was clicked
        for i, n in enumerate(suggested_clicks):
            if n:
                return suggested_children[i]
        return chat_value

# --- Transaction Details Modal Callbacks ---
def make_json_safe(d):
    safe = {}
    for k, v in d.items():
        if isinstance(v, (pd.Timestamp, pd.Period)):
            safe[k] = str(v)
        else:
            safe[k] = v
    return safe

@app.callback(
    [Output('selected-transaction', 'data'), Output('transaction-details-modal', 'is_open')],
    [Input({'type': 'transaction-btn', 'index': ALL}, 'n_clicks')],
    [State('month-dropdown-store', 'data')],
    prevent_initial_call=True
)
def open_transaction_modal(n_clicks_list, month_store):
    selected_month = month_store.get("value") if month_store else None
    ctx = callback_context
    if not ctx.triggered or not any(n_clicks_list):
        raise dash.exceptions.PreventUpdate
    # Get the index of the button that was actually clicked
    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    if not triggered:
        raise dash.exceptions.PreventUpdate
    try:
        triggered_idx = int(eval(triggered)['index'])
    except Exception:
        raise dash.exceptions.PreventUpdate
    clicked_idx = triggered_idx
    # Get the transaction data for the clicked index
    month_df = df[df["month"].astype(str) == selected_month].reset_index(drop=True)
    if clicked_idx >= len(month_df):
        raise dash.exceptions.PreventUpdate
    tx_data = month_df.iloc[clicked_idx].to_dict()
    tx_data = make_json_safe(tx_data)
    return tx_data, True

@app.callback(
    Output('transaction-details-body', 'children'),
    [Input('selected-transaction', 'data')],
    prevent_initial_call=True
)
def render_transaction_details(tx_data):
    if not tx_data:
        return "No transaction selected."
    # Extract fields with fallback
    merchant = tx_data.get('merchant', 'N/A')
    amount = tx_data.get('amount', 'N/A')
    currency = tx_data.get('currency', '')
    date = tx_data.get('transactionTimestamp', '')
    address = tx_data.get('address', tx_data.get('description', ''))
    logo = tx_data.get('merchant_logo', '')
    category = tx_data.get('category', 'N/A')
    category_logo = tx_data.get('category_logo', '')
    lat = tx_data.get('lat', None)
    long = tx_data.get('long', None)
    co2 = tx_data.get('co2FootprintValue', None)
    co2_unit = tx_data.get('co2FootprintUnit', '')
    url = tx_data.get('url', None)
    tags = tx_data.get('tags', '')
    # Debug print for map
    print(f"DEBUG: lat={lat}, long={long}")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    map_img = None
    if lat and long and GOOGLE_MAPS_API_KEY:
        try:
            lat_f = float(lat)
            long_f = float(long)
            map_url = (
                f"https://maps.googleapis.com/maps/api/staticmap"
                f"?center={lat_f},{long_f}&zoom=15&size=416x234"
                f"&markers=color:red%7C{lat_f},{long_f}&key={GOOGLE_MAPS_API_KEY}"
            )
            print(f"DEBUG: map_url={map_url}")
            map_link = f"https://www.google.com/maps/search/?api=1&query={lat_f},{long_f}"
            map_img = html.A(
                html.Img(
                    src=map_url,
                    style={
                        "width": "100%",
                        "height": "100%",
                        "objectFit": "cover",
                        "borderRadius": "0.7em",
                        "boxShadow": "0 4px 24px rgba(56,217,150,0.10)"
                    }
                ),
                href=map_link,
                target="_blank",
                style={"display": "block"}
            )
            map_container = html.Div(
                map_img,
                style={
                    "width": "100%",
                    "aspectRatio": "16 / 9",
                    "margin": "1.5em auto 0.5em auto",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "overflow": "hidden"
                }
            )
        except Exception as e:
            print(f"DEBUG: map error: {e}")
            map_img = None
            map_container = None
        
    else:
        map_container = None
    # Format date
    try:
        date_str = pd.to_datetime(date).strftime('%B %d, %Y at %I:%M %p')
    except Exception:
        date_str = str(date)
    # Localized currency formatting
    currency_symbols = {
        "GBP": "£",
        "EUR": "€",
        "USD": "$",
        "CZK": "Kč",
        "PLN": "zł",
        "HUF": "Ft",
        "RON": "lei",
        "AUD": "$",
        "CAD": "$",
        "CHF": "Fr.",
        "SEK": "kr",
        "NOK": "kr",
        "DKK": "kr",
        "JPY": "¥",
        "CNY": "¥",
        "SGD": "$",
        "INR": "₹",
        # Add more as needed
    }
    symbol = currency_symbols.get(currency, currency)
    try:
        amount_str = f"{float(amount):,.2f}"
    except Exception:
        amount_str = str(amount)
    if symbol in ["£", "€", "$", "¥", "₹"]:
        display_amount = f"{symbol}{amount_str}"
    elif symbol in ["Kč", "zł", "Ft", "lei", "Fr.", "kr"]:
        display_amount = f"{amount_str} {symbol}"
    else:
        display_amount = f"{amount_str} {symbol}"
    # Map embed (OpenStreetMap Static Image)
    # CO2 badge
    co2_badge = None
    if co2 is not None:
        co2_badge = html.Div([
            html.Span("🌱", style={"fontSize": "1.3em", "marginRight": "0.3em"}),
            html.Span(f"{co2} {co2_unit} CO₂", style={"fontWeight": 600})
        ], style={"color": "#38d996", "background": "#1e293b", "padding": "0.4em 1em", "borderRadius": "1em", "display": "inline-flex", "alignItems": "center", "marginBottom": "1em", "fontSize": "1.1em"})
    # Tags
    tag_list = [t.strip() for t in tags.replace('{','').replace('}','').replace('"','').replace("'","").split(',') if t.strip()]
    tag_badges = [dbc.Badge(t, color="info", className="me-1", style={"fontSize": "1em", "background": "#4f8cff", "color": "#fff"}) for t in tag_list]
    # --- Redesigned Transaction Details Layout ---
    # Left column: Amount, merchant, date, category, CO2, tags
    left_col = [
        html.Div([
            html.H1(display_amount, style={"color": "#38d996", "fontWeight": 900, "fontSize": "2.5em", "margin": 0, "textShadow": "0 2px 8px #0008", "lineHeight": "1.1"}),
            html.Img(
                src=logo,
                style={
                    "height": "3.5em", "width": "3.5em", "objectFit": "cover", "borderRadius": "50%", "boxShadow": "0 0 20px #4f8cff99", "background": "#fff", "marginLeft": "1em", "border": "3px solid #38d996", "verticalAlign": "middle"
                }
            ) if logo else None,
        ], style={"display": "flex", "alignItems": "center", "gap": "1em", "marginBottom": "0.2em"}),
        html.H2(merchant, style={"color": "#fff", "fontWeight": 800, "fontSize": "1.3em", "margin": 0, "marginBottom": "0.1em", "lineHeight": "1.1"}),
        html.Div(date_str, style={"color": "#b0c4de", "fontSize": "1em", "marginBottom": "0.3em"}),
        html.Div([
            html.Img(src=category_logo, style={"height": "1.2em", "width": "1.2em", "objectFit": "contain", "borderRadius": "0.3em", "background": "#fff", "marginRight": "0.3em", "verticalAlign": "middle"}) if category_logo else None,
            html.Span(category, style={"fontWeight": 600, "fontSize": "1em", "color": "#38d996", "verticalAlign": "middle"})
        ], style={"display": "inline-flex", "alignItems": "center", "marginBottom": "0.2em", "background": "rgba(56,217,150,0.08)", "borderRadius": "0.7em", "padding": "0.2em 0.7em", "width": "fit-content"}) if category else None,
        html.Div(co2_badge, style={"width": "fit-content"}) if co2_badge else None,
        html.Div(tag_badges, style={"marginBottom": "0.3em"}) if tag_badges else None,
    ]
    # Right column: Small map, action buttons below
    right_col = [
        map_container,
        html.Div([
            dbc.Button("Contact", color="light", outline=True, className="me-2", style={"marginRight": "0.5em", "color": "#38d996", "borderColor": "#38d996"}),
            dbc.Button("Website", color="light", outline=True, href=url if url else None, target="_blank", style={"color": "#4f8cff", "borderColor": "#4f8cff", "pointerEvents": "auto" if url else "none", "opacity": 1 if url else 0.5})
        ], style={"display": "flex", "justifyContent": "center", "gap": "0.5em", "marginTop": "1em"})
    ]
    children = [
        dbc.Row([
            dbc.Col(left_col, width=8, style={"textAlign": "left", "display": "flex", "flexDirection": "column", "justifyContent": "flex-start", "gap": "0.2em"}),
            dbc.Col(right_col, width=4, style={"textAlign": "right", "display": "flex", "flexDirection": "column", "alignItems": "flex-end", "justifyContent": "flex-start", "gap": "0.2em"})
        ], align="center", className="g-0"),
        html.Hr(style={"borderColor": "#38d99633", "margin": "0.7em 0"}),
    ]
    return html.Div([
        html.Div(style={
            "height": "6px", "width": "100%", "background": "linear-gradient(90deg, #4f8cff 0%, #38d996 100%)", "borderTopLeftRadius": "1em", "borderTopRightRadius": "1em", "marginBottom": "-1em"
        }),
        dbc.Card(children, body=True, style={
            "padding": "1.2em 1.2em 1em 1.2em",
            "background": "rgba(30, 41, 59, 0.95)",
            "borderRadius": "1em",
            "boxShadow": "0 8px 32px #0006",
            "backdropFilter": "blur(8px)",
            "border": "1px solid #38d99633",
            "width": "100%",
            "margin": "0"
        })
    ], style={"background": "none", "padding": "0.5em 0 0 0"})

# Add a callback to toggle the dropdown open/close
@app.callback(
    Output("month-dropdown-store", "data"),
    Input("month-dropdown-selected", "n_clicks"),
    State("month-dropdown-store", "data"),
    prevent_initial_call=True
)
def toggle_month_dropdown(n_clicks, store):
    if not store:
        store = {"open": False, "value": None}
    # Toggle open state
    store = store.copy()
    store["open"] = not store.get("open", False)
    return store

# Add a callback to select a month and close the dropdown, and reset n_clicks for all options
@app.callback(
    [Output("month-dropdown-store", "data", allow_duplicate=True)] +
    [Output({"type": "month-dropdown-option", "value": o["value"]}, "n_clicks") for o in month_options],
    Input({"type": "month-dropdown-option", "value": ALL}, "n_clicks"),
    State("month-dropdown-store", "data"),
    prevent_initial_call=True
)
def select_month_dropdown(option_clicks, store):
    ctx = callback_context
    if not ctx.triggered or not store:
        return [dash.no_update] + [0 for _ in option_clicks]
    # Find which option was clicked
    for i, n in enumerate(option_clicks):
        if n:
            triggered_id = ctx.inputs_list[0][i]["id"]
            value = triggered_id["value"]
            store = store.copy()
            store["value"] = value
            store["open"] = False
            # Reset all n_clicks to 0
            return [store] + [0 for _ in option_clicks]
    return [dash.no_update] + [0 for _ in option_clicks]

# Add a callback to update the selected month label in the dropdown
@app.callback(
    Output("month-dropdown-selected", "children"),
    Input("month-dropdown-store", "data"),
    prevent_initial_call=False
)
def update_month_dropdown_label(store):
    value = store.get("value") if store else None
    label = next((o["label"] for o in month_options if o["value"] == value), value)
    # Chevron span (keep as before)
    chevron = html.Span(
        html.Span("", id="month-chevron", style={"display": "inline-block", "marginLeft": "0.7em", "transition": "transform 0.3s"}),
        style={"display": "inline-block", "verticalAlign": "middle"}
    )
    return [label, chevron]

# Update the dropdown list style based on open/close state
@app.callback(
    Output("month-dropdown-list", "style"),
    Input("month-dropdown-store", "data"),
    State("month-dropdown-list", "style"),
    prevent_initial_call=False
)
def update_dropdown_list_style(store, base_style):
    style = dict(base_style) if base_style else {}
    if store and store.get("open"):
        style["opacity"] = 1
        style["pointerEvents"] = "auto"
        style["transform"] = "translateY(0)"
    else:
        style["opacity"] = 0
        style["pointerEvents"] = "none"
        style["transform"] = "translateY(-10px)"
    return style


if __name__ == "__main__":
    app.run(debug=True)