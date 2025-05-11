import streamlit as st
from scanner import scan_market
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner")

tab1, tab2, tab3 = st.tabs(["🔍 Live Signals", "📊 Signal History", "📈 Performance Report"])

# --- TAB 1: Live Signals ---
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

# --- TAB 2: Signal History ---
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

# --- TAB 3: Performance Report ---
with tab3:
    st.subheader("📈 Performance Report")
    if os.path.exists("signals_log.csv"):
        df = pd.read_csv("signals_log.csv")
        df = df[df["result"].isin([0, 1])]
        df["signal_time"] = pd.to_datetime(df["signal_time"], errors="coerce")
        df["hour"] = df["signal_time"].dt.hour
        df["weekday"] = df["signal_time"].dt.day_name()

        total = len(df)
        wins = df["result"].sum()
        losses = total - wins
        win_rate = (wins / total * 100) if total else 0
        avg_conf = df["confidence"].mean()

        st.metric("Total Signals", total)
        st.metric("TP Hit", wins)
        st.metric("SL Hit", losses)
        st.metric("Win Rate", f"{win_rate:.2f}%")
        st.metric("Avg Confidence", f"{avg_conf:.1f}%")

        st.subheader("📊 Confidence Distribution")
        st.bar_chart(df["confidence"])

        st.subheader("📅 Win Rate by Hour")
        hour_stats = df.groupby("hour")["result"].mean() * 100
        st.bar_chart(hour_stats)

        st.subheader("📅 Win Rate by Day of Week")
        day_stats = df.groupby("weekday")["result"].mean() * 100
        st.bar_chart(day_stats)

        st.subheader("🪙 Signal Count by Coin")
        coin_stats = df["symbol"].value_counts()
        st.bar_chart(coin_stats)
    else:
        st.warning("No signals with results to analyze yet.")
