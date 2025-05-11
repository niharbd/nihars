import streamlit as st
from scanner import scan_market
from datetime import datetime
import pytz

st.set_page_config(page_title="Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

with st.spinner("⏳ Scanning market..."):
    df, scan_time = scan_market()

st.markdown(f"🕒 **Last Scanned:** `{scan_time}` BST")
st.markdown("⏱️ Auto-refresh every 10 minutes (via UptimeRobot ping)")

st.divider()

if df.empty:
    st.warning("⚠️ No high-confidence signals found.")
else:
    for _, row in df.iterrows():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"🪙 {row['Coin']} - {row['Type']}")
            st.write(f"**Detected:** {row['Why Detected']}")
            st.write(f"**Signal Time:** `{row['Signal Time']}`")
        with col2:
            st.metric("Confidence", f"{row['Confidence']}%")
        with col3:
            st.success(f"TP: {row['TP']}  \nSL: {row['SL']}")
