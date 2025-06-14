import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน")

# กำหนด path ของไฟล์ CSV
csv_path = './data/youtube_comments_full.csv'

# ตรวจสอบว่าไฟล์มีอยู่จริง
if not os.path.exists(csv_path):
    st.error(f"ไม่พบไฟล์ CSV ที่ {csv_path}")
else:
    # เชื่อมต่อ DuckDB และโหลดข้อมูล
    con = duckdb.connect()

    # สร้าง view จากไฟล์ CSV
    con.execute(f"""
        CREATE OR REPLACE VIEW comments AS
        SELECT
            *,
            strptime(published_at, '%Y-%m-%d %H:%M:%S') AS timestamp,
            strftime(published_at, '%Y-%m') AS year_month
        FROM read_csv_auto('{csv_path}')
    """)

    # ดึงข้อมูลจำนวนคอมเมนต์ตามเดือนและชื่อวิดีโอ
    df = con.execute("""
        SELECT
            year_month,
            video_title,
            COUNT(*) AS comment_count
        FROM comments
        GROUP BY year_month, video_title
        ORDER BY year_month
    """).fetchdf()

    # แสดงวิดีโอที่มีใน dropdown
    unique_videos = df["video_title"].unique()
    selected_video = st.selectbox("🎬 เลือกวิดีโอ", unique_videos)

    # กรองเฉพาะข้อมูลของวิดีโอที่เลือก
    filtered_df = df[df["video_title"] == selected_video]

    # วาดกราฟด้วย Plotly
    fig = px.line(
        filtered_df,
        x="year_month",
        y="comment_count",
        title=f"จำนวนคอมเมนต์ต่อเดือนของวิดีโอ: {selected_video}",
        labels={"year_month": "เดือน", "comment_count": "จำนวนคอมเมนต์"},
        markers=True
    )

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

