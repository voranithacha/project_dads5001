import pandas as pd
import streamlit as st
import os

# === PATH CONFIG ===
CSV_PATH = './data/youtube_comments_full.csv'

st.subheader("🧾 ความคิดเห็นจาก YouTube")

# === FILE CHECK ===
if not os.path.exists(CSV_PATH):
    st.error(f"ไม่พบไฟล์ที่ {CSV_PATH}")
else:
    df = pd.read_csv(CSV_PATH)

    if "comment_text_display" not in df.columns:
        st.error("ไม่พบคอลัมน์ 'comment_text_display' ในไฟล์ CSV นี้")
    else:
        # === Show only the DataFrame ===
        st.dataframe(df[["comment_text_display"]].dropna().reset_index(drop=True))
