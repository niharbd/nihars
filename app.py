<<<<<<< HEAD
import streamlit as st
import pandas as pd
from datetime import datetime
from scanner import scan_market

# Set up Streamlit page
st.set_page_config(page_title="📈 Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

# Fetch signals
signals = scan_market()

if not signals or signals.empty:
    st.info("No valid breakout or breakdown signals detected right now.")
else:
    st.markdown("### ✅ High Confidence Signals (≥80%)")

    styled_df = signals.style.format({
        "Entry": "{:.4f}",
        "TP1": "{:.4f}",
        "TP2": "{:.4f}",
        "TP3": "{:.4f}",
        "SL": "{:.4f}",
    })
    st.dataframe(styled_df)

# Auto-refresh every 10 minutes
st.markdown(
    f"<script>setTimeout(function(){{window.location.reload();}}, {10 * 60 * 1000});</script>",
    unsafe_allow_html=True
)
=======
import streamlit as st
import pandas as pd
from datetime import datetime
from scanner import scan_market

# Set up Streamlit page
st.set_page_config(page_title="📈 Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

# Fetch signals
signals = scan_market()

if not signals or signals.empty:
    st.info("No valid breakout or breakdown signals detected right now.")
else:
    st.markdown("### ✅ High Confidence Signals (≥80%)")

    styled_df = signals.style.format({
        "Entry": "{:.4f}",
        "TP1": "{:.4f}",
        "TP2": "{:.4f}",
        "TP3": "{:.4f}",
        "SL": "{:.4f}",
    })
    st.dataframe(styled_df)

# Auto-refresh every 10 minutes
st.markdown(
    f"<script>setTimeout(function(){{window.location.reload();}}, {10 * 60 * 1000});</script>",
    unsafe_allow_html=True
)
>>>>>>> b6dff15fd799cb879acde10f8f4ccf15e5bf28ea
