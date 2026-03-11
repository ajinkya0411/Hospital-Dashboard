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

# -------------------- Razorpay Key --------------------
RAZORPAY_KEY = "rzp_test_SPQhDnYPGZQtWo"

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

        dcc.Store(id="payment-success"),

        # ================= NAVBAR =================
        html.Div(
            style={
                "backgroundColor": "#0b3c5d",
                "padding": "18px 60px",
                "color": "white",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
            },

            children=[
                html.H3("CityCare Multispeciality Hospital"),
                html.Div("Patient Wallet Dashboard")
            ]
        ),

        # ================= MAIN =================
        html.Div(

            style={
                "padding": "50px",
                "maxWidth": "1400px",
                "margin": "auto"
            },

            children=[

                # ================= WALLET =================
                html.Div(

                    style={
                        "background": "white",
                        "padding": "30px",
                        "borderRadius": "10px",
                        "boxShadow": "0 5px 15px rgba(0,0,0,0.1)"
                    },

                    children=[

                        html.H4("Wallet Recharge"),

                        html.Br(),

                        html.Label("Patient ID"),

                        dcc.Input(
                            id="patient_id",
                            placeholder="PAT-XXXX",
                            style={"width": "100%", "padding": "10px"}
                        ),

                        html.Br(), html.Br(),

                        html.Label("Recharge Amount (₹)"),

                        dcc.Input(
                            id="amount",
                            type="number",
                            placeholder="Minimum ₹100",
                            style={"width": "100%", "padding": "10px"}
                        ),

                        html.Br(), html.Br(),

                        html.Button(
                            "Pay with Razorpay",
                            id="razorpay-btn",
                            n_clicks=0,
                            style={
                                "padding": "12px",
                                "backgroundColor": "#198754",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "width": "100%"
                            }
                        ),

                        html.Br(), html.Br(),

                        html.Button(
                            "Refresh Balance",
                            id="check_btn",
                            n_clicks=0,
                            style={
                                "padding": "12px",
                                "backgroundColor": "#0b3c5d",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "width": "100%"
                            }
                        ),

                        html.Div(
                            id="message",
                            style={"marginTop": "20px", "fontWeight": "600"}
                        )
                    ]
                ),

                html.Br(), html.Br(),

                # ================= BALANCE =================
                html.Div(

                    style={
                        "background": "#0b3c5d",
                        "color": "white",
                        "padding": "30px",
                        "borderRadius": "10px"
                    },

                    children=[

                        html.P("Available Wallet Balance"),

                        html.H2(
                            id="balance_output",
                            children="₹ 0"
                        )
                    ]
                ),

                html.Br(), html.Br(),

                # ================= TRANSACTIONS =================
                html.Div(

                    style={
                        "background": "white",
                        "padding": "30px",
                        "borderRadius": "10px",
                        "boxShadow": "0 5px 15px rgba(0,0,0,0.1)"
                    },

                    children=[

                        html.H4("Transaction History"),

                        html.Br(),

                        dash_table.DataTable(

                            id="transaction_table",

                            columns=[
                                {"name": "Date & Time", "id": "time"},
                                {"name": "Type", "id": "type"},
                                {"name": "Source", "id": "source"},
                                {"name": "Amount", "id": "amount"},
                                {"name": "Balance", "id": "balance"},
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# -------------------- Razorpay Popup --------------------
app.clientside_callback(
    f"""
    function(n_clicks) {{

        if (!n_clicks) {{
            return "";
        }}

        var amount = document.getElementById("amount").value;

        if (!amount || amount < 100) {{
            alert("Minimum recharge ₹100");
            return "";
        }}

        var options = {{

            "key": "rzp_test_SPQhDnYPGZQtWo",
            "amount": amount * 100,
            "currency": "INR",
            "name": "CityCare Hospital",
            "description": "Wallet Recharge",

            "handler": function (response) {{

                alert("Payment Successful: " + response.razorpay_payment_id);

                window.dash_clientside.callback_context
                .triggered[0].value = response.razorpay_payment_id;

            }},

            "theme": {{
                "color": "#0b3c5d"
            }}
        }};

        var rzp = new Razorpay(options);
        rzp.open();

        return "";
    }}
    """,
    Output("message", "children"),
    Input("razorpay-btn", "n_clicks")
)

# -------------------- Wallet Logic --------------------
@app.callback(

    [Output("balance_output", "children"),
     Output("transaction_table", "data"),
     Output("message", "children")],

    Input("check_btn", "n_clicks"),

    State("patient_id", "value")

)
def check_balance(n, patient_id):

    if not patient_id:
        return "₹ 0", [], "Enter Patient ID"

    wallet_ref = db.collection("wallets").document(str(patient_id))
    doc = wallet_ref.get()

    if not doc.exists:

        wallet_ref.set({
            "balance": 0,
            "transactions": []
        })

        balance = 0
        txns = []

    else:

        data = doc.to_dict()
        balance = data.get("balance", 0)
        txns = data.get("transactions", [])

    return f"₹ {balance}", txns, "Balance refreshed"


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=10000)

    
