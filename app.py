<<<<<<< HEAD
import streamlit as st
import pandas as pd
from scanner import scan_market

st.set_page_config(page_title="📈 Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

# Fetch signals
signals = scan_market()

# Display signal time and auto-refresh info
st.markdown("🔄 Updated every 10 minutes. Showing real-time signals (BST).")

# If no signals
if signals.empty:
    st.info("No valid breakout or breakdown signals detected right now.")
else:
    st.dataframe(signals.style.format({
        "Entry": "{:.4f}", "TP": "{:.4f}", "SL": "{:.4f}"
    }), use_container_width=True)

    st.markdown("✅ Only coins with RSI, EMA and volume confirmation logic shown.")
=======
import streamlit as st
import pandas as pd
from scanner import scan_market

st.set_page_config(page_title="📈 Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

# Fetch signals
signals = scan_market()

# Display signal time and auto-refresh info
st.markdown("🔄 Updated every 10 minutes. Showing real-time signals (BST).")

# If no signals
if signals.empty:
    st.info("No valid breakout or breakdown signals detected right now.")
else:
    st.dataframe(signals.style.format({
        "Entry": "{:.4f}", "TP": "{:.4f}", "SL": "{:.4f}"
    }), use_container_width=True)

    st.markdown("✅ Only coins with RSI, EMA and volume confirmation logic shown.")
>>>>>>> 0b5850d12ca4fedb8addea987bc32f06bbc76a8a
