import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# -------------------- Firebase Setup --------------------
cred = credentials.Certificate("firebase_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------- Dash App --------------------
app = dash.Dash(__name__)
app.title = "Patient Wallet | CityCare Hospital"

# -------------------- Layout --------------------
app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "backgroundColor": "#eef1f5",
        "fontFamily": "Segoe UI, Arial",
    },
    children=[

        # ================= NAVBAR =================
        html.Div(
            style={
                "backgroundColor": "#0b3c5d",
                "padding": "18px 60px",
                "color": "white",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
            },
            children=[
                html.Div([
                    html.H3("CityCare Multispeciality Hospital",
                            style={"margin": "0", "fontWeight": "600"}),
                    html.Small("Patient Financial Services",
                               style={"opacity": "0.8"})
                ]),
                html.Div("Patient Wallet Dashboard",
                         style={"fontSize": "15px", "opacity": "0.9"})
            ]
        ),

        # ================= MAIN CONTENT =================
        html.Div(
            style={
                "padding": "50px 70px",
                "maxWidth": "1600px",
                "margin": "auto"
            },
            children=[

                # -------- TOP SECTION --------
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1.3fr 0.7fr",
                        "gap": "40px"
                    },
                    children=[

                        # ===== Wallet Recharge Card =====
                        html.Div(
                            style={
                                "background": "white",
                                "padding": "35px",
                                "borderRadius": "10px",
                                "boxShadow": "0 8px 20px rgba(0,0,0,0.08)"
                            },
                            children=[
                                html.H4("Wallet Recharge",
                                        style={"marginBottom": "5px"}),
                                html.Small(
                                    "Add funds securely to patient wallet",
                                    style={"color": "#6c757d"}
                                ),
                                html.Hr(style={"margin": "20px 0"}),

                                html.Label("Patient ID",
                                           style={"fontWeight": "600"}),
                                dcc.Input(
                                    id="patient_id",
                                    placeholder="PAT-XXXX",
                                    style={
                                        "width": "100%",
                                        "padding": "12px",
                                        "borderRadius": "6px",
                                        "border": "1px solid #ced4da"
                                    }
                                ),

                                html.Br(), html.Br(),

                                html.Label("Recharge Amount (₹)",
                                           style={"fontWeight": "600"}),
                                dcc.Input(
                                    id="amount",
                                    type="number",
                                    placeholder="Minimum ₹100",
                                    style={
                                        "width": "100%",
                                        "padding": "12px",
                                        "borderRadius": "6px",
                                        "border": "1px solid #ced4da"
                                    }
                                ),

                                html.Br(), html.Br(),

                                html.Label("Payment Method",
                                           style={"fontWeight": "600"}),
                                dcc.Dropdown(
                                    id="payment_source",
                                    options=[
                                        {"label": "Google Pay (UPI)", "value": "GPay"},
                                        {"label": "Paytm Wallet", "value": "Paytm"},
                                        {"label": "BHIM UPI", "value": "BHIM"},
                                    ],
                                    placeholder="Select payment option",
                                    style={"borderRadius": "6px"}
                                ),

                                html.Br(),

                                html.Div(
                                    style={"display": "flex", "gap": "20px"},
                                    children=[
                                        html.Button(
                                            "Add Money",
                                            id="recharge_btn",
                                            n_clicks=0,
                                            style={
                                                "flex": "1",
                                                "padding": "14px",
                                                "backgroundColor": "#198754",
                                                "color": "white",
                                                "border": "none",
                                                "borderRadius": "6px",
                                                "fontSize": "15px",
                                                "fontWeight": "600",
                                                "cursor": "pointer"
                                            }
                                        ),
                                        html.Button(
                                            "Refresh Balance",
                                            id="check_btn",
                                            n_clicks=0,
                                            style={
                                                "flex": "1",
                                                "padding": "14px",
                                                "backgroundColor": "#0b3c5d",
                                                "color": "white",
                                                "border": "none",
                                                "borderRadius": "6px",
                                                "fontSize": "15px",
                                                "fontWeight": "600",
                                                "cursor": "pointer"
                                            }
                                        )
                                    ]
                                ),

                                html.Div(
                                    id="message",
                                    style={
                                        "marginTop": "18px",
                                        "fontWeight": "600"
                                    }
                                )
                            ]
                        ),

                        # ===== Balance Summary Card =====
                        html.Div(
                            style={
                                "background": "linear-gradient(135deg,#0b3c5d,#3282b8)",
                                "padding": "40px",
                                "borderRadius": "12px",
                                "color": "white",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.18)",
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center"
                            },
                            children=[
                                html.P("Available Wallet Balance",
                                       style={"opacity": "0.85", "fontSize": "15px"}),
                                html.H1(
                                    id="balance_output",
                                    children="₹ 0",
                                    style={
                                        "marginTop": "10px",
                                        "fontWeight": "700",
                                        "letterSpacing": "1px"
                                    }
                                ),
                                html.P(
                                    "Valid for OPD, pharmacy, diagnostics & services",
                                    style={"marginTop": "12px", "fontSize": "14px"}
                                )
                            ]
                        )
                    ]
                ),

                html.Br(), html.Br(),

                # ================= TRANSACTION TABLE =================
                html.Div(
                    style={
                        "background": "white",
                        "padding": "35px",
                        "borderRadius": "10px",
                        "boxShadow": "0 8px 20px rgba(0,0,0,0.08)"
                    },
                    children=[
                        html.H4("Transaction History",
                                style={"marginBottom": "5px"}),
                        html.Small(
                            "Complete wallet transaction audit trail",
                            style={"color": "#6c757d"}
                        ),
                        html.Hr(style={"margin": "20px 0"}),

                        dash_table.DataTable(
                            id="transaction_table",
                            columns=[
                                {"name": "Date & Time", "id": "time"},
                                {"name": "Transaction Type", "id": "type"},
                                {"name": "Source", "id": "source"},
                                {"name": "Amount (₹)", "id": "amount"},
                                {"name": "Balance After (₹)", "id": "balance"},
                            ],
                            style_cell={
                                "textAlign": "center",
                                "padding": "12px",
                                "fontSize": "14px",
                                "border": "1px solid #dee2e6"
                            },
                            style_header={
                                "backgroundColor": "#0b3c5d",
                                "color": "white",
                                "fontWeight": "700"
                            },
                            style_data_conditional=[
                                {
                                    "if": {"filter_query": '{type} = "CREDIT"'},
                                    "color": "#198754",
                                    "fontWeight": "600"
                                },
                                {
                                    "if": {"filter_query": '{type} = "DEBIT"'},
                                    "color": "#dc3545",
                                    "fontWeight": "600"
                                }
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# -------------------- Callback Logic (UNCHANGED) --------------------
@app.callback(
    [Output("message", "children"),
     Output("balance_output", "children"),
     Output("transaction_table", "data")],
    [Input("recharge_btn", "n_clicks"),
     Input("check_btn", "n_clicks")],
    State("patient_id", "value"),
    State("amount", "value"),
    State("payment_source", "value")
)
def wallet_actions(recharge, check, patient_id, amount, source):

    if not patient_id:
        return "Patient ID required", "₹ 0", []

    wallet_ref = db.collection("wallets").document(str(patient_id))
    doc = wallet_ref.get()

    if not doc.exists:
        wallet_ref.set({"balance": 0, "transactions": []})
        balance = 0
        txns = []
    else:
        data = doc.to_dict()
        balance = data.get("balance", 0)
        txns = data.get("transactions", [])

    triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if triggered == "recharge_btn":
        if not amount or amount < 100 or not source:
            return "Minimum ₹100 & payment method required", f"₹ {balance}", txns

        balance += amount
        txn = {
            "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "type": "CREDIT",
            "source": source,
            "amount": amount,
            "balance": balance
        }
        txns.insert(0, txn)

        wallet_ref.update({"balance": balance, "transactions": txns})
        return "Wallet recharged successfully", f"₹ {balance}", txns

    return "Balance refreshed", f"₹ {balance}", txns


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8051)
