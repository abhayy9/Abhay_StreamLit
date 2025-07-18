import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import time

# Set Streamlit app config (styling and layout)
st.set_page_config(page_title="Volvo Funds Terminal", layout="wide")

# Custom styling (futuristic design)
page_style = """
<style>
    .stApp {
        background-color: #121212;
        background-image: linear-gradient(to right, #141414, #1e1e1e);
        font-family: 'Fira Code', monospace;
        color: #f1f1f1;
    }
    .stDataFrame div {
        font-size: 15px;
        color: #e8e8e8 !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 12px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stMarkdown p {
        color: #e8e8e8 !important;
    }
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

st.title("🧠 Volvo Funds Hedge Operations Terminal")

# Define the list of stocks in your portfolio (replace with your own holdings)
portfolio = [
    {"Instrument": "AVANTEL", "Qty": 180, "Avg_cost": 194.00},
    {"Instrument": "CGPOWER", "Qty": 50, "Avg_cost": 689.37},
    {"Instrument": "DAMCAPITAL", "Qty": 53, "Avg_cost": 283.00},
    {"Instrument": "GMDCLTD", "Qty": 68, "Avg_cost": 429.73},
    {"Instrument": "GMRAIRPORT", "Qty": 285, "Avg_cost": 94.43},
    {"Instrument": "HAL", "Qty": 10, "Avg_cost": 4948.35},
    {"Instrument": "HCC", "Qty": 207, "Avg_cost": 39.79},
    {"Instrument": "IRB", "Qty": 400, "Avg_cost": 66.04},
    {"Instrument": "IREDA", "Qty": 210, "Avg_cost": 241.75},
    {"Instrument": "IRFC", "Qty": 36, "Avg_cost": 183.34},
    {"Instrument": "JKPAPER", "Qty": 80, "Avg_cost": 401.95},
    {"Instrument": "KSB", "Qty": 30, "Avg_cost": 987.56},
    {"Instrument": "NBCC", "Qty": 352, "Avg_cost": 99.45},
    {"Instrument": "NTPC", "Qty": 1, "Avg_cost": 416.00},
    {"Instrument": "ONGC", "Qty": 89, "Avg_cost": 280.15},
    {"Instrument": "TATAMOTORS", "Qty": 25, "Avg_cost": 961.20},
    {"Instrument": "TATAPOWER", "Qty": 107, "Avg_cost": 447.09}
]

# Fetch real-time stock data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_prices(symbols):
    data = yf.download(tickers=" ".join(symbols), period="2d", interval="1d")
    
    if data.empty:
        return {}, {}

    close_today = data['Close'].iloc[-1]  # Today's closing price
    close_yesterday = data['Close'].iloc[-2]  # Yesterday's closing price
    return close_today.to_dict(), close_yesterday.to_dict()


# Function to log buy/sell transactions
def log_transaction(transaction_log, ticker, qty, price, action):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    transaction_log.append({
        "Date": now,
        "Stock": ticker,
        "Qty": qty,
        "Price": price,
        "Action": action
    })

# Display portfolio and handle user input
# Function to display portfolio and handle user input
def display_portfolio(label_prefix, transaction_log, all_data):
    custom_data = []
    st.sidebar.header(f"🔧 {label_prefix} Portfolio Input")
    num_stocks = st.sidebar.number_input(f"{label_prefix}: How many stocks?", min_value=1, max_value=20, value=1, key=f"num_{label_prefix}")
    
    for i in range(num_stocks):
        st.sidebar.markdown(f"### {label_prefix} Stock #{i+1}")
        ticker = st.sidebar.text_input(f"{label_prefix} Ticker {i+1}", key=f"ticker_{label_prefix}_{i}")
        qty = st.sidebar.number_input(f"{label_prefix} Qty {i+1}", key=f"qty_{label_prefix}_{i}", min_value=0)
        avg_price = st.sidebar.number_input(f"{label_prefix} Avg Price {i+1}", key=f"price_{label_prefix}_{i}", min_value=0.0)
        action = st.sidebar.selectbox(f"{label_prefix} Action {i+1}", ["Buy", "Sell"], key=f"action_{label_prefix}_{i}")
        
        if ticker and qty > 0:
            log_transaction(transaction_log, ticker.upper(), qty, avg_price, action)
            custom_data.append({"Instrument": ticker.upper(), "Qty": qty, "Avg_cost": avg_price})

    if custom_data:
        df = pd.DataFrame(custom_data)
        symbols = [row['Instrument'] for row in custom_data]
        current_prices, previous_prices = fetch_prices(symbols)

        if not current_prices:
            st.warning("No valid stock data available.")
            return  # Exit the function if data is not available

        df["LTP"] = df["Instrument"].map(current_prices)
        df["Prev_Close"] = df["Instrument"].map(previous_prices)
        
        # Check if LTP is correctly assigned
        if df["LTP"].isnull().any():
            st.warning("Some stocks couldn't retrieve their LTP data.")
            return

        df["Trend"] = df.apply(lambda x: "🟢 Up" if x["LTP"] > x["Prev_Close"] else ("🔴 Down" if x["LTP"] < x["Prev_Close"] else "⚪ Flat"), axis=1)
        df["Invested"] = df["Qty"] * df["Avg_cost"]
        df["Current_Value"] = df["Qty"] * df["LTP"]
        df["P&L"] = df["Current_Value"] - df["Invested"]
        df["Return_%"] = (df["P&L"] / df["Invested"]) * 100
        df["Target"] = df["Avg_cost"] * 1.15
        df["Stop_Loss"] = df["Avg_cost"] * 0.90
        df["Target_P&L"] = (df["Target"] - df["Avg_cost"]) * df["Qty"]
        df["SL_Risk"] = (df["Avg_cost"] - df["Stop_Loss"]) * df["Qty"]

        bonus_text = df["Trend"].apply(lambda t: "📈 Gaining Momentum!" if "Up" in t else ("📉 Under Pressure!" if "Down" in t else ""))
        bonus_color = df["Trend"].apply(lambda t: "green" if "Up" in t else ("red" if "Down" in t else "#999"))

        st.subheader(f"📊 {label_prefix} Tactical Matrix")
        st.dataframe(df.style.format({
            "Avg_cost": "₹{:.2f}", "LTP": "₹{:.2f}", "Invested": "₹{:.2f}",
            "Current_Value": "₹{:.2f}", "P&L": "₹{:.2f}", "Return_%": "{:.2f}%",
            "Target": "₹{:.2f}", "Stop_Loss": "₹{:.2f}", "Target_P&L": "₹{:.2f}", "SL_Risk": "₹{:.2f}"
        }), use_container_width=True)

        st.markdown("### 🎯 Movement Highlights")
        for i in range(len(df)):
            if bonus_text[i]:
                st.markdown(f"<span style='color:{bonus_color[i]}; font-size: 18px; font-weight: bold;'>» {df['Instrument'][i]}: {bonus_text[i]}</span>", unsafe_allow_html=True)

        # Adding this portfolio data to the global collection
        all_data.append(df)

    else:
        st.info(f"Please enter at least one stock for {label_prefix} Portfolio.")

# Display Master Portfolio (Aggregating Values)
def display_master_portfolio(all_data):
    if all_data:
        # Aggregating the values across all portfolios
        full_df = pd.concat(all_data, ignore_index=True)
        aggregated_values = full_df[["Invested", "Current_Value", "P&L", "Return_%"]].sum()
        st.subheader("📊 Master Portfolio Overview")
        st.markdown(f"**Total Invested:** ₹{aggregated_values['Invested']:.2f}")
        st.markdown(f"**Total Current Value:** ₹{aggregated_values['Current_Value']:.2f}")
        st.markdown(f"**Total P&L:** ₹{aggregated_values['P&L']:.2f}")
        st.markdown(f"**Total Return (%):** {aggregated_values['Return_%']:.2f}%")
    else:
        st.info("No portfolios to aggregate yet!")

# Tabs for multiple portfolios
tab1, tab2, tab3 = st.tabs(["📁 Portfolio 1", "📁 Portfolio 2", "📁 Portfolio 3"])

# Create storage for transaction logs and data
transaction_logs = []
all_portfolio_data = []

with tab1:
    display_portfolio("Portfolio 1", transaction_logs, all_portfolio_data)

with tab2:
    display_portfolio("Portfolio 2", transaction_logs, all_portfolio_data)

with tab3:
    display_portfolio("Portfolio 3", transaction_logs, all_portfolio_data)

# Display aggregated values in Master Portfolio
st.subheader("📊 Master Portfolio Aggregated View")
display_master_portfolio(all_portfolio_data)
