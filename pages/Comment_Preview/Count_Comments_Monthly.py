import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน")

# กำหนด path ของไฟล์ CSV
csv_path = './data/youtube_comments_fullxx.csv'
 
# ตรวจสอบว่าไฟล์มีอยู่หรือไม่
if os.path.exists(csv_path):
    # โหลดข้อมูลจาก CSV
    df = pd.read_csv(csv_path)
 
    # แสดงตัวอย่างข้อมูล 5 แถวแรก
    st.dataframe(df.head())
else:
    st.error(f"ไม่พบไฟล์ที่ตำแหน่ง: {csv_path}")

