import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน")

# กำหนด path ของไฟล์ CSV
csv_path = './data/youtube_comments_full.csv'

# ตรวจสอบว่าไฟล์มีอยู่จริงก่อนโหลด
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    st.write(f"✅ พบข้อมูลจำนวน {len(df)} แถว")
    
    # แสดงตารางข้อมูล
    st.dataframe(df)

else:
    st.error(f"ไม่พบไฟล์ CSV ที่ path: `{csv_path}`")


