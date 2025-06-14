import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

st.subheader("⌨ จำนวนการแสดงความคิดเห็นในเเต่ละเดือน")

# โหลดข้อมูล
con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")  # เผื่อคุณอยากใช้ในอนาคต

# แทนที่ path ด้านล่างนี้ให้ถูกต้อง
csv_path = './data/youtube_comments_full.csv'

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
