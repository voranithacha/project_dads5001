import pandas as pd
import streamlit as st
import plotly.express as px
import os

def run():
    # === PATH CONFIG ===
    CSV_PATH = './data/youtube_comments_full.csv'
    st.subheader("⌨ จำนวนการแสดงความคิดเห็นในเเต่ละเดือน")
    
    # === FILE CHECK ===
    if not os.path.exists(CSV_PATH):
        st.error(f"ไม่พบไฟล์ที่ {CSV_PATH}")
        return

    # === LOAD CSV ===
    df = pd.read_csv(CSV_PATH)

    if "comment_text_display" not in df.columns:
        st.error("ไม่พบคอลัมน์ 'comment_text_display' ในไฟล์ CSV นี้")
        return

    # === PREPROCESS DATE ===
    if "published_at" in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        df = df.dropna(subset=['published_at'])  # ลบแถวที่มีวันที่ไม่ถูกต้อง
        df['year_month'] = df['published_at'].dt.to_period('M').astype(str)  # เช่น 2025-04
    else:
        st.error("ไม่พบคอลัมน์ 'published_at' ในไฟล์ CSV")
        return

    # === COUNT COMMENTS ===
    comment_counts = df.groupby(['year_month', 'video_title']).size().reset_index(name='comment_count')

    # === PLOT WITH PLOTLY ===
    fig = px.line(
        comment_counts,
        x='year_month',
        y='comment_count',
        color='video_title',
        markers=True,
        title='จำนวนคอมเมนต์ในแต่ละเดือน แยกตามชื่อวิดีโอ',
        #labels={
        #    'year_month': 'เดือน',
        #    'comment_count': 'จำนวนคอมเมนต์',
        #    'video_title': 'ชื่อวิดีโอ'
        #}
    )
    fig.update_layout(xaxis=dict(tickangle=45))
    st.plotly_chart(fig, use_container_width=True)

    # === OPTIONAL: SHOW RAW DATA ===
    with st.expander("📋 ดูข้อมูลดิบ"):
        st.dataframe(comment_counts)


            




