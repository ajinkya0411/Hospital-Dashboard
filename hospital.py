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
app = dash.Dash(
    __name__,
    external_scripts=["https://checkout.razorpay.com/v1/checkout.js"]
)
server = app.server
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
                                html.H4("Wallet Recharge"),
                                html.Hr(),

                                html.Label("Patient ID"),
                                dcc.Input(id="patient_id",
                                          placeholder="PAT-XXXX",
                                          style={"width": "100%", "padding": "10px"}),

                                html.Br(), html.Br(),

                                html.Label("Recharge Amount (₹)"),
                                dcc.Input(id="amount",
                                          type="number",
                                          placeholder="Minimum ₹100",
                                          style={"width": "100%", "padding": "10px"}),

                                html.Br(), html.Br(),

                                html.Label("Payment Method"),
                                dcc.Dropdown(
                                    id="payment_source",
                                    options=[
                                        {"label": "Google Pay (UPI)", "value": "GPay"},
                                        {"label": "Paytm Wallet", "value": "Paytm"},
                                        {"label": "BHIM UPI", "value": "BHIM"},
                                    ],
                                    placeholder="Select payment option"
                                ),

                                html.Br(),

                                html.Div(
                                    style={"display": "flex", "gap": "20px"},
                                    children=[

                                        # Razorpay Payment Button
                                        html.Button(
                                            "Pay with Razorpay",
                                            id="razorpay-btn",
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
                                                "borderRadius": "6px"
                                            }
                                        )
                                    ]
                                ),

                                html.Div(id="message",
                                         style={"marginTop": "18px",
                                                "fontWeight": "600"})
                            ]
                        ),

                        # ===== Balance Summary Card =====
                        html.Div(
                            style={
                                "background": "linear-gradient(135deg,#0b3c5d,#3282b8)",
                                "padding": "40px",
                                "borderRadius": "12px",
                                "color": "white"
                            },
                            children=[
                                html.P("Available Wallet Balance"),
                                html.H1(id="balance_output", children="₹ 0"),
                                html.P("Valid for hospital services")
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

                        html.H4("Transaction History"),
                        html.Hr(),

                        dash_table.DataTable(
                            id="transaction_table",
                            columns=[
                                {"name": "Date & Time", "id": "time"},
                                {"name": "Transaction Type", "id": "type"},
                                {"name": "Source", "id": "source"},
                                {"name": "Amount (₹)", "id": "amount"},
                                {"name": "Balance After (₹)", "id": "balance"},
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# -------------------- Razorpay Client Callback --------------------
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) { return ""; }

        var options = {
            "key": "rzp_test_SPQhDnYPGZQtWo",
            "amount": 50000,
            "currency": "INR",
            "name": "CityCare Hospital",
            "description": "Patient Wallet Recharge",
            "handler": function (response){
                alert("Payment Successful: " + response.razorpay_payment_id);
            },
            "theme": {"color": "#0b3c5d"}
        };

        var rzp = new Razorpay(options);
        rzp.open();
        return "";
    }
    """,
    Output("message", "children"),
    Input("razorpay-btn", "n_clicks")
)

# -------------------- Wallet Callback --------------------
@app.callback(
    [Output("message", "children"),
     Output("balance_output", "children"),
     Output("transaction_table", "data")],
    [Input("check_btn", "n_clicks")],
    State("patient_id", "value")
)
def check_balance(check, patient_id):

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

    return "Balance refreshed", f"₹ {balance}", txns


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=10000)
    