import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from urllib.parse import parse_qs

# ---------------- Firebase ----------------
cred = credentials.Certificate("firebase_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- Validate Admin ----------------
def validate_admin(uid):
    try:
        user_doc = db.collection("users").document(uid).get()
        return user_doc.exists and user_doc.to_dict().get("role") == "admin"
    except:
        return False

# ---------------- Dash App ----------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# ---------------- Styles ----------------
CARD_STYLE = {
    "background": "#ffffff",
    "padding": "20px",
    "borderRadius": "12px",
    "boxShadow": "0px 4px 12px rgba(0,0,0,0.08)",
    "marginBottom": "20px"
}

INPUT_STYLE = {
    "width": "100%",
    "padding": "10px",
    "marginBottom": "10px",
    "borderRadius": "8px",
    "border": "1px solid #ccc"
}

BUTTON_STYLE = {
    "background": "#007BFF",
    "color": "white",
    "padding": "10px",
    "border": "none",
    "borderRadius": "8px",
    "width": "100%",
    "fontWeight": "bold",
    "cursor": "pointer"
}

# ---------------- Layout ----------------
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page_content')
])

# ---------------- Page Loader ----------------
@app.callback(
    Output('page_content', 'children'),
    Input('url', 'search')
)
def load_dashboard(search):

    query = parse_qs(search.lstrip("?"))
    uid = query.get("uid", [None])[0]

    if not uid or not validate_admin(uid):
        return html.Div(
            style={"padding": "100px", "textAlign": "center"},
            children=[
                html.H2("❌ Unauthorized Access"),
                html.P("You are not allowed to access Admin Dashboard.")
            ]
        )

    return html.Div(style={"display": "flex", "fontFamily": "Arial"}, children=[

        # -------- Sidebar --------
        html.Div(style={
            "width": "220px",
            "background": "#1e293b",
            "color": "white",
            "height": "100vh",
            "padding": "20px"
        }, children=[
            html.H2("🏥 Admin", style={"marginBottom": "30px"}),
            html.P("Dashboard"),
            html.P("Patients"),
            html.P("Transactions"),
        ]),

        # -------- Main Content --------
        html.Div(style={"flex": 1, "padding": "30px", "background": "#f1f5f9"}, children=[

            html.H2("Admin Dashboard", style={"marginBottom": "20px"}),

            # ---- Action Card ----
            html.Div(style=CARD_STYLE, children=[
                html.H4("💳 Deduct Patient Wallet"),

                dcc.Input(id="admin_patient_id", placeholder="Patient ID", style=INPUT_STYLE),

                dcc.Dropdown(
                    id="service_type",
                    placeholder="Select Service",
                    options=[
                        {"label": "OPD", "value": "OPD"},
                        {"label": "Lab", "value": "Lab"},
                        {"label": "Pharmacy", "value": "Pharmacy"}
                    ],
                    style={"marginBottom": "10px"}
                ),

                dcc.Input(id="deduct_amount", type="number", placeholder="Amount", style=INPUT_STYLE),

                html.Button("Deduct Amount", id="deduct_btn", style=BUTTON_STYLE),

                html.Div(id="admin_message", style={"marginTop": "10px", "color": "green"})
            ]),

            # ---- Table Card ----
            html.Div(style=CARD_STYLE, children=[
                html.H4("📊 Patient Wallet Overview"),

                dash_table.DataTable(
                    id="wallet_table",
                    columns=[
                        {"name": "Patient ID", "id": "patient_id"},
                        {"name": "Balance", "id": "balance"},
                        {"name": "Last Txn", "id": "last_txn"},
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px"
                    },
                    style_header={
                        "backgroundColor": "#007BFF",
                        "color": "white",
                        "fontWeight": "bold"
                    }
                )
            ])

        ])
    ])

# ---------------- Callback ----------------
@app.callback(
    [Output("admin_message", "children"),
     Output("wallet_table", "data")],
    Input("deduct_btn", "n_clicks"),
    State("admin_patient_id", "value"),
    State("service_type", "value"),
    State("deduct_amount", "value")
)
def admin_actions(n_clicks, patient_id, service, amount):

    wallets = db.collection("wallets").stream()
    table_data = []

    for w in wallets:
        data = w.to_dict()
        txns = data.get("transactions", [])
        last_txn = txns[0]["time"] if txns else "-"
        table_data.append({
            "patient_id": w.id,
            "balance": data.get("balance", 0),
            "last_txn": last_txn
        })

    if not n_clicks:
        return "", table_data

    if not patient_id or not service or not amount:
        return "⚠️ Invalid input", table_data

    ref = db.collection("wallets").document(patient_id)
    doc = ref.get()

    if not doc.exists:
        return "❌ Wallet not found", table_data

    data = doc.to_dict()
    balance = data["balance"]

    if balance < amount:
        return "❌ Insufficient balance", table_data

    balance -= amount
    txns = data["transactions"]

    txns.insert(0, {
        "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "type": "DEBIT",
        "source": service,
        "amount": amount,
        "balance": balance
    })

    ref.update({"balance": balance, "transactions": txns})

    return "✅ Deducted successfully", table_data


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=8060)
