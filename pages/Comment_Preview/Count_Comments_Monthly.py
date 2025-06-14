import pandas as pd
import streamlit as st
import os

# === PATH CONFIG ===
CSV_PATH = './data/youtube_comments_full.csv'

st.subheader("📄 แสดงข้อมูลจากไฟล์ความคิดเห็น YouTube (CSV)")

# === FILE CHECK ===
if not os.path.exists(CSV_PATH):
    st.error(f"❌ ไม่พบไฟล์ที่ {CSV_PATH}")
else:
    df = pd.read_csv(CSV_PATH)

    st.success(f"✅ โหลดข้อมูลสำเร็จ! พบ {len(df)} แถว และ {len(df.columns)} คอลัมน์")
    
    # แสดงข้อมูล
    st.dataframe(df, use_container_width=True)

    # ถ้าต้องการ preview เฉพาะ 10 แถวแรก:
    # st.dataframe(df.head(10))
