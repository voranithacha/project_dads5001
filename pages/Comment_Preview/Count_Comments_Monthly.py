import pandas as pd
import streamlit as st
import os
import duckdb
import plotly.express as px

def run():
          # === PATH CONFIG ===
          csv_path = './data/youtube_comments_full.csv'
          # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
          if os.path.exists(csv_path):
              # โหลดข้อมูลจาก CSV
              df = pd.read_csv(csv_path)
           
              # แสดงตัวอย่างข้อมูล 5 แถวแรก
              st.dataframe(df.head())
          else:
              st.error(f"ไม่พบไฟล์ที่ตำแหน่ง: {csv_path}")
  
 




