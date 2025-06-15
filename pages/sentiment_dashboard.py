import streamlit as st
import pandas as pd
import duckdb as db
import plotly.express as px
from transformers import pipeline
import matplotlib.pyplot as plt
import re
import os

# --- การตั้งค่าหน้าเว็บ Streamlit ---
st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- ฟังก์ชันช่วย ---

@st.cache_resource
def load_sentiment_model():
    """โหลดโมเดลวิเคราะห์อารมณ์จาก Hugging Face"""
    st.info("กำลังโหลดโมเดล AI... (ครั้งแรกอาจใช้เวลาสักครู่)")
    try:
        # ใช้โมเดลภาษาไทยที่ให้ผลลัพธ์เป็น Negative/Neutral/Positive
        model_name = "poom-sci/WangchanBERTa-finetuned-sentiment"
        
        # ตรวจสอบว่ามี GPU หรือไม่ และใช้ device ที่เหมาะสม
        import torch
        if torch.cuda.is_available():
            device = 0 
            st.info("ตรวจพบ GPU: จะใช้ GPU ในการประมวลผลโมเดล")
        else:
            device = -1
            st.warning("ไม่พบ GPU: จะใช้ CPU ในการประมวลผลโมเดล ซึ่งอาจใช้เวลานานกว่า")

        sentiment_pipeline = pipeline(model=model_name, device=device)
        st.success(f"โหลดโมเดล AI '{model_name}' สำเร็จแล้ว!")
        return sentiment_pipeline
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดโมเดล AI: {e}")
        st.error("โปรดตรวจสอบ: 1. การเชื่อมต่ออินเทอร์เน็ต 2. ชื่อโมเดลถูกต้อง (อาจลองเปลี่ยนเป็นตัวอื่น) 3. หากเป็น Private Repo ต้อง Login Hugging Face 4. การติดตั้ง PyTorch/TensorFlow และ CUDA หากใช้ GPU")
        st.stop()

@st.cache_data
def analyze_sentiment(df, _sentiment_pipeline): 
    """ทำความสะอาดข้อมูลและวิเคราะห์ความรู้สึกของคอมเมนต์"""
    def preprocess_text(text):
        if not isinstance(text, str):
            return ""
        text = re.sub(r'http\S+', '', text)  
        text = re.sub(r'<.*?>', '', text) 
        text = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s]', '', text) 
        return text.strip()

    df['cleaned_comment'] = df['comment'].apply(preprocess_text)
    
    valid_comments_df = df[df['cleaned_comment'].str.len() > 0].copy()
    
    if not valid_comments_df.empty:
        results = _sentiment_pipeline(
            valid_comments_df['cleaned_comment'].tolist(), 
            top_k=1, 
            batch_size=64, 
            truncation=True,  
            padding=True      
        ) 
        
        sentiments = [res[0]['label'] for res in results]
        valid_comments_df['sentiment'] = sentiments
        
        df = df.merge(valid_comments_df[['sentiment']], left_index=True, right_index=True, how='left')
        df['sentiment'].fillna('neutral', inplace=True)

        # *** เพิ่มโค้ดตรงนี้: รวม 'neu' และ 'neutral' ***
        df['sentiment'] = df['sentiment'].replace('neu', 'neutral')
        # *** สิ้นสุดการเพิ่มโค้ด ***

    else:
        df['sentiment'] = 'neutral'
        st.warning("ไม่พบคอมเมนต์ที่สามารถวิเคราะห์ได้หลังจากทำความสะอาด")

    return df

# *** ฟังก์ชัน generate_wordcloud ถูกลบออกไปแล้ว ***

# --- ส่วนแสดงผลของแดชบอร์ด ---

st.title("📊 Sentiment Analysis Dashboard (YouTube Comments)")

duckdb_file_path = './comment.duckdb'
if not os.path.exists(duckdb_file_path):
    st.error(f"ไม่พบไฟล์ฐานข้อมูล '{duckdb_file_path}' ในโฟลเดอร์ปัจจุบัน")
    st.info("โปรดตรวจสอบให้แน่ใจว่าไฟล์ 'comment.duckdb' อยู่ในโฟลเดอร์เดียวกับสคริปต์")
    st.stop()

try:
    con = db.connect(duckdb_file_path)
    # พิจารณาสุ่มตัวอย่างข้อมูลถ้ามีจำนวนมาก เพื่อลดเวลาการรันครั้งแรก
    # คุณสามารถเปิดคอมเมนต์บรรทัดนี้ได้หากต้องการสุ่มตัวอย่าง
    # df_original = con.execute("SELECT comment_text_original as comment FROM yt_comment_full ORDER BY RANDOM() LIMIT 10000;").fetchdf()
    df_original = con.execute("SELECT comment_text_original as comment FROM yt_comment_full;").fetchdf()
    con.close()
    
    st.success(f"โหลดข้อมูลสำเร็จ! พบ {len(df_original)} คอมเมนต์")

    sentiment_pipeline = load_sentiment_model()

    df_analyzed = analyze_sentiment(df_original.copy(), sentiment_pipeline)

    # ---
    st.header("สรุปภาพรวมอารมณ์ (Emotion Analysis)")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        sentiment_counts = df_analyzed['sentiment'].value_counts()
        if not sentiment_counts.empty:
            # กำหนดสีสำหรับแต่ละอารมณ์ (ไม่บังคับ แต่ช่วยให้กราฟสวยงาม)
            color_map = {
                'positive': 'green', 
                'neutral': 'grey', # ตอนนี้รวม neu เข้ามาแล้ว
                'negative': 'red'
            }
            # ตรวจสอบว่ามีคีย์ใน color_map ตรงกับ sentiment_counts.index
            colors = [color_map.get(s, '#CCCCCC') for s in sentiment_counts.index] 

            fig_pie = px.pie(
                sentiment_counts, 
                values=sentiment_counts.values, 
                names=sentiment_counts.index,
                title='สัดส่วนอารมณ์โดยรวม',
                hole=0.3,
                color=sentiment_counts.index, 
                color_discrete_map=color_map 
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("ไม่มีข้อมูลอารมณ์ที่จะแสดงในแผนภูมิวงกลม")


    with col2:
        if not sentiment_counts.empty:
            st.dataframe(sentiment_counts)
        else:
            st.warning("ไม่มีข้อมูลอารมณ์ที่จะแสดงในตาราง")

    # ---

    st.header("ตารางข้อมูลพร้อมผลการวิเคราะห์")
    if not df_analyzed.empty:
        st.dataframe(df_analyzed[['comment', 'sentiment']])
    else:
        st.warning("ไม่พบข้อมูลคอมเมนต์ที่ผ่านการวิเคราะห์")


except db.IOException as e:
    st.error(f"ไม่สามารถเชื่อมต่อหรืออ่านไฟล์ 'comment.duckdb' ได้")
    st.error(f"รายละเอียดข้อผิดพลาด: {e}")
    st.info("โปรดตรวจสอบว่าไฟล์ 'comment.duckdb' ไม่เสีย และคุณมีสิทธิ์ในการอ่านไฟล์นั้น")
except db.CatalogException as e:
    st.error(f"ไม่พบตารางหรือคอลัมน์ที่ระบุในไฟล์ 'comment.duckdb'")
    st.error(f"รายละเอียดข้อผิดพลาด: {e}")
    st.info("โปรดตรวจสอบว่ามีตารางชื่อ 'yt_comment_full' และคอลัมน์ 'comment_text_original' ในไฟล์ 'comment.duckdb'")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
    st.info("โปรดลองตรวจสอบโค้ดและข้อมูลของคุณอีกครั้ง")
