
import streamlit as st
from scanner import scan_market
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner")

# Tabs
tab1, tab2 = st.tabs(["🔍 Live Signals", "📊 Signal History"])

with tab1:
    with st.spinner("Scanning Binance Futures..."):
        signals, scan_time = scan_market()

    st.markdown(f"🕒 **Last Scanned:** `{scan_time}` BST")
    st.info("Only signals with ML confidence ≥ 80% are shown.")
    st.divider()

    if signals.empty:
        st.warning("⚠️ No high-confidence signals found.")
    else:
        for _, row in signals.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.subheader(f"🪙 {row['Coin']} - {row['Type']}")
                st.write(f"**Detected by:** {row['Why Detected']}")
                st.write(f"🕒 Signal Time: `{row['Signal Time']}`")
                st.write(f"**Entry Price:** `{row['Entry']}`")
            with col2:
                st.metric("Confidence", f"{row['Confidence']}%")
            with col3:
                st.success(f"TP: {row['TP']}  \nSL: {row['SL']}")

with tab2:
    st.subheader("📊 Signal Log & Results")
    if os.path.exists("signals_log.csv"):
        df_log = pd.read_csv("signals_log.csv")
        filter_option = st.selectbox("Filter by Result", ["All", "TP Hit (1)", "SL Hit (0)", "Unresolved"])
        if filter_option == "TP Hit (1)":
            df_log = df_log[df_log["result"] == 1]
        elif filter_option == "SL Hit (0)":
            df_log = df_log[df_log["result"] == 0]
        elif filter_option == "Unresolved":
            df_log = df_log[df_log["result"].isna() | (df_log["result"] == "")]

        st.dataframe(df_log)

        csv = df_log.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "signals_log.csv", "text/csv")
    else:
        st.warning("No signal log found yet.")
