import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from scanner import scan_market

st.set_page_config(page_title="📈 Nihar's Signal Scanner", layout="wide")
st.title("📈 Nihar's Signal Scanner (Live Trading)")

raw_signals = scan_market()
signals_df = pd.DataFrame(raw_signals)

BST = pytz.timezone("Asia/Dhaka")
now_bst = datetime.now(BST).strftime("%Y-%m-%d %H:%M:%S")

if not signals_df.empty:
    signals_df['signal_time'] = now_bst
    signals_df = signals_df[signals_df['confidence'] >= 80]
    signals_df = signals_df[[
        'symbol', 'type', 'confidence', 'entry', 'tp', 'sl', 'reason', 'signal_time'
    ]]

if signals_df.empty:
    st.info("No valid breakout or breakdown signals detected right now.")
else:
    st.dataframe(signals_df)

st.markdown(
    "<script>setTimeout(function(){window.location.reload();}, 600000);</script>",
    unsafe_allow_html=True
)
