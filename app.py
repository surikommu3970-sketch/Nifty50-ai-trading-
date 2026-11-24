
from streamlit_autorefresh import st_autorefresh

import streamlit as st

st.set_page_config(
    page_title="NIFTY 50 AI Options",
    page_icon="📈",
    layout="wide"
)

st_autorefresh(interval=5000, key="nifty_refresh")

st.title("📈 NIFTY 50 AI Options Trading")
st.caption("CALL BUY + PUT BUY | Paper Trading Only")

st.sidebar.header("Trading Settings")

lots = st.sidebar.number_input(
    "Number of Lots", min_value=1, value=1
)

lot_size = st.sidebar.number_input(
    "Option Lot Size (verify current contract)",
    min_value=1, value=1
)

sl_pct = st.sidebar.number_input(
    "Stop Loss %", min_value=0.1, value=20.0
)

target_pct = st.sidebar.number_input(
    "Target %", min_value=0.1, value=40.0
)

st.subheader("Market Indicators")

c1, c2 = st.columns(2)

with c1:
    ema9 = st.number_input("EMA 9", value=100.0)
    ema21 = st.number_input("EMA 21", value=99.0)
    price = st.number_input("NIFTY Price", value=100.0)

with c2:
    vwap = st.number_input("VWAP", value=99.0)
    rsi = st.number_input("RSI", value=56.0)
    adx = st.number_input("ADX", value=25.0)

volume_ok = st.checkbox("Volume Confirmation", value=True)

if ema9 > ema21 and price > vwap and rsi > 55 and adx > 20 and volume_ok:
    signal = "CALL BUY"
elif ema9 < ema21 and price < vwap and rsi < 45 and adx > 20 and volume_ok:
    signal = "PUT BUY"
else:
    signal = "NO TRADE"

if signal == "CALL BUY":
    st.success("🟢 CALL BUY SIGNAL")
elif signal == "PUT BUY":
    st.error("🔴 PUT BUY SIGNAL")
else:
    st.warning("🟡 NO TRADE")

st.subheader("Option Premium")

ce_price = st.number_input(
    "CE Premium", min_value=0.0, value=100.0
)
pe_price = st.number_input(
    "PE Premium", min_value=0.0, value=100.0
)

if "position" not in st.session_state:
    st.session_state.position = None

if "trades" not in st.session_state:
    st.session_state.trades = []


# Automatic Paper Trading
if "position" not in st.session_state:
    st.session_state.position = None

if "trades" not in st.session_state:
    st.session_state.trades = []

if "last_entry_signal" not in st.session_state:
    st.session_state.last_entry_signal = None

# Reset entry lock when signal disappears
if signal == "NO TRADE":
    st.session_state.last_entry_signal = None

# Automatic BUY
elif (
    st.session_state.position is None
    and signal != st.session_state.last_entry_signal
):
    entry = ce_price if signal == "CALL BUY" else pe_price

    st.session_state.position = {
        "type": "CE" if signal == "CALL BUY" else "PE",
        "entry": entry,
        "quantity": lots * lot_size,
        "sl": entry * (1 - sl_pct / 100),
        "target": entry * (1 + target_pct / 100)
    }

    st.session_state.last_entry_signal = signal
    st.success("Automatic Paper BUY created!")

# Position monitoring
pos = st.session_state.position

if pos is not None:
    current = ce_price if pos["type"] == "CE" else pe_price
    pnl = (current - pos["entry"]) * pos["quantity"]

    st.subheader("Open Paper Position")
    st.write("Option:", pos["type"])
    st.write("Entry:", pos["entry"])
    st.write("Current Premium:", current)
    st.write("Quantity:", pos["quantity"])
    st.write("Stop Loss:", round(pos["sl"], 2))
    st.write("Target:", round(pos["target"], 2))
    st.metric("Paper P&L", f"₹{pnl:.2f}")

    # Automatic SELL
    exit_reason = None

    if current <= pos["sl"]:
        exit_reason = "Stop Loss"
    elif current >= pos["target"]:
        exit_reason = "Target"

    if exit_reason:
        st.session_state.trades.append({
            "Option": pos["type"],
            "Entry": pos["entry"],
            "Exit": current,
            "Quantity": pos["quantity"],
            "P&L": pnl,
            "Reason": exit_reason
        })

        st.session_state.position = None
        st.success(f"Automatic SELL: {exit_reason} reached!")

    elif st.button("PAPER SELL / EXIT"):
        st.session_state.trades.append({
            "Option": pos["type"],
            "Entry": pos["entry"],
            "Exit": current,
            "Quantity": pos["quantity"],
            "P&L": pnl,
            "Reason": "Manual Exit"
        })

        st.session_state.position = None
        st.success("Paper position closed!")
    
st.subheader("Trade History")
if st.session_state.trades:
    st.dataframe(st.session_state.trades)
else:
    st.info("No completed trades yet.")

st.caption(
    "Simulation only. No live market data or real broker orders."
          )
