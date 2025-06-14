import pandas as pd
import streamlit as st
import os
import duckdb
import plotly.express as px

def run():
  # === PATH CONFIG ===
  csv_path = './data/youtube_comments_full.csv'
  
  st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน (CSV)")
  # โหลดข้อมูล
  con = duckdb.connect()
  con.execute("INSTALL sqlite; LOAD sqlite;")  # เผื่อคุณอยากใช้ในอนาคต
  
  # สร้าง view จาก CSV โดยตรง
  con.execute(f"""
      CREATE OR REPLACE VIEW comments AS
      SELECT
          *,
          strptime(published_at, '%Y-%m-%d %H:%M:%S') AS timestamp,
          strftime(published_at, '%Y-%m') AS year_month
      FROM read_csv_auto('{csv_path}')
  """)
  
  # ดึงข้อมูลจำนวน comment แยกตามเดือนและชื่อวิดีโอ
  df = con.execute("""
      SELECT
          year_month,
          video_title,
          COUNT(*) AS comment_count
      FROM comments
      GROUP BY year_month, video_title
      ORDER BY year_month
  """).fetchdf()
  
  # วาดกราฟด้วย Plotly Express
  fig = px.line(
      df,
      x='year_month',
      y='comment_count',
      color='video_title',
      title='จำนวน Comment ต่อเดือน แยกตามชื่อวิดีโอ',
      labels={
          'year_month': 'ปี-เดือน',
          'comment_count': 'จำนวน Comment',
          'video_title': 'ชื่อวิดีโอ'
      },
      markers=True
  )
  
  fig.update_layout(xaxis=dict(tickangle=45))
  fig.show()




