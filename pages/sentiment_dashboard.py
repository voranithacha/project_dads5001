import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import plotly.express as px
import plotly.graph_objects as go
import duckdb as db
import numpy as np
from collections import Counter
import re
from typing import List, Tuple, Dict
import time

st.set_page_config(page_title="แดชบอร์ดวิเคราะห์ความรู้สึก", layout="wide")
st.title("🔍 แดชบอร์ดวิเคราะห์ความรู้สึกขั้นสูง (ความคิดเห็น YouTube)")

# === อัลกอริทึม 1: การประมวลผลแบบแบทช์เพื่อประสิทธิภาพ ===
class BatchSentimentAnalyzer:
    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.tokenizer = None
        self.model = None
        self.labels_map = {0: "เชิงลบ", 1: "เป็นกลาง", 2: "เชิงบวก"}
        
    @st.cache_resource(show_spinner=True)
    def load_model(_self):
        """โหลดโมเดลพร้อมแคชเพื่อประสิทธิภาพ"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(_self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(_self.model_name, num_labels=3)
            return tokenizer, model
        except Exception as e:
            st.error(f"ข้อผิดพลาดในการโหลดโมเดล: {str(e)}")
            return None, None
    
    def preprocess_text(self, text: str) -> str:
        """ทำความสะอาดและประมวลผลข้อความสำหรับการวิเคราะห์ที่ดีขึ้น"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        # ลบช่องว่างเกินและอักขระพิเศษ
        text = re.sub(r'\s+', ' ', text.strip())
        # จำกัดความยาวเพื่อหลีกเลี่ยงปัญหาหน่วยความจำ
        return text[:512]
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """อัลกอริทึมการทำนายแบบแบทช์เพื่อประสิทธิภาพ"""
        if not self.tokenizer or not self.model:
            self.tokenizer, self.model = self.load_model()
            
        if not self.tokenizer or not self.model:
            return [("เป็นกลาง", 0.0)] * len(texts)
        
        # ประมวลผลข้อความ
        clean_texts = [self.preprocess_text(text) for text in texts]
        
        # แปลงเป็น Token แบบแบทช์
        inputs = self.tokenizer(
            clean_texts, 
            return_tensors="pt", 
            truncation=True, 
            padding=True,
            max_length=512
        )
        
        # ทำนาย
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            predictions = torch.argmax(probs, dim=1)
            confidence_scores = torch.max(probs, dim=1)[0]
        
        results = []
        for pred, conf in zip(predictions, confidence_scores):
            results.append((self.labels_map[pred.item()], conf.item()))
        
        return results
    
    def analyze_sentiments(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """อัลกอริทึมหลักในการวิเคราะห์ความรู้สึกพร้อมติดตามความคืบหน้า"""
        texts = df[text_column].tolist()
        total_batches = len(texts) // self.batch_size + (1 if len(texts) % self.batch_size else 0)
        
        all_sentiments = []
        all_confidences = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_results = self.predict_batch(batch_texts)
            
            for sentiment, confidence in batch_results:
                all_sentiments.append(sentiment)
                all_confidences.append(confidence)
            
            # อัพเดทความคืบหน้า
            current_batch = i // self.batch_size + 1
            progress = current_batch / total_batches
            progress_bar.progress(progress)
            status_text.text(f"กำลังประมวลผลแบทช์ {current_batch}/{total_batches}")
        
        progress_bar.empty()
        status_text.empty()
        
        df_result = df.copy()
        df_result['sentiment'] = all_sentiments
        df_result['confidence'] = all_confidences
        
        return df_result

# === อัลกอริทึม 2: การโหลดข้อมูลพร้อมการจัดการข้อผิดพลาด ===
@st.cache_data
def load_data_from_duckdb(db_path: str, table_name: str) -> pd.DataFrame:
    """การโหลดข้อมูลที่ปรับปรุงแล้วพร้อมการจัดการข้อผิดพลาด"""
    try:
        con = db.connect(db_path)
        
        # ตรวจสอบว่าตารางมีอยู่หรือไม่
        tables_query = "SHOW TABLES;"
        tables_df = con.execute(tables_query).fetchdf()
        
        if table_name not in tables_df['name'].values:
            st.error(f"❌ ไม่พบตาราง '{table_name}' ในฐานข้อมูล")
            return pd.DataFrame()
        
        # โหลดข้อมูลพร้อมจำกัดจำนวนสำหรับการทดสอบเบื้องต้น
        query = f"SELECT comment_text_original as comment FROM {table_name} LIMIT 1000;"
        df = con.execute(query).fetchdf()
        con.close()
        
        return df
        
    except Exception as e:
        st.error(f"❌ ข้อผิดพลาดฐานข้อมูล: {str(e)}")
        return pd.DataFrame()

# === อัลกอริทึม 3: การวิเคราะห์ทางสถิติ ===
def calculate_sentiment_statistics(df: pd.DataFrame) -> Dict:
    """คำนวณสถิติความรู้สึกที่ครอบคลุม"""
    stats = {}
    
    # การนับพื้นฐาน
    sentiment_counts = df['sentiment'].value_counts()
    stats['counts'] = sentiment_counts.to_dict()
    stats['percentages'] = (sentiment_counts / len(df) * 100).round(2).to_dict()
    
    # สถิติความเชื่อมั่น
    stats['avg_confidence'] = df['confidence'].mean()
    stats['confidence_by_sentiment'] = df.groupby('sentiment')['confidence'].agg(['mean', 'std']).round(3)
    
    # การทำนายที่มีความเชื่อมั่นสูง
    high_confidence_threshold = 0.8
    stats['high_confidence_count'] = len(df[df['confidence'] > high_confidence_threshold])
    stats['high_confidence_percentage'] = (stats['high_confidence_count'] / len(df) * 100)
    
    return stats

# === อัลกอริทึม 4: คุณสมบัติการวิเคราะห์ข้อความ ===
def analyze_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """สกัดคุณสมบัติข้อความเพื่อการวิเคราะห์เชิงลึก"""
    df_analysis = df.copy()
    
    # การวิเคราะห์ความยาวข้อความ
    df_analysis['text_length'] = df_analysis['comment'].astype(str).str.len()
    df_analysis['word_count'] = df_analysis['comment'].astype(str).str.split().str.len()
    
    # การตรวจจับอีโมจิและอักขระพิเศษ
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿⚠-⚡]')
    df_analysis['has_emoji'] = df_analysis['comment'].astype(str).str.contains(emoji_pattern, regex=True)
    df_analysis['emoji_count'] = df_analysis['comment'].astype(str).str.count(emoji_pattern)
    
    # เครื่องหมายอัศเจรีย์และเครื่องหมายคำถาม
    df_analysis['exclamation_count'] = df_analysis['comment'].astype(str).str.count('!')
    df_analysis['question_count'] = df_analysis['comment'].astype(str).str.count('?')
    
    return df_analysis

# === แอปพลิเคชันหลัก ===
def main():
    st.sidebar.header("⚙️ การตั้งค่า")
    
    # ตัวเลือกการตั้งค่า
    db_path = st.sidebar.text_input("เส้นทางฐานข้อมูล", value="./comment.duckdb")
    table_name = st.sidebar.text_input("ชื่อตาราง", value="yt_comment_full")
    batch_size = st.sidebar.slider("ขนาดแบทช์", min_value=8, max_value=64, value=32)
    model_name = st.sidebar.selectbox(
        "โมเดล", 
        ["airesearch/wangchanberta-base-wiki", "cardiffnlp/twitter-roberta-base-sentiment-latest"]
    )
    
    # โหลดข้อมูล
    st.header("📊 การโหลดข้อมูล")
    df = load_data_from_duckdb(db_path, table_name)
    
    if df.empty:
        st.warning("ไม่มีข้อมูลโหลด กรุณาตรวจสอบการตั้งค่าฐานข้อมูลของคุณ")
        return
    
    st.success(f"✅ โหลด {len(df)} ความคิดเห็นจากฐานข้อมูลเรียบร้อยแล้ว")
    
    # เริ่มต้นตัววิเคราะห์
    analyzer = BatchSentimentAnalyzer(model_name, batch_size)
    
    # วิเคราะห์ความรู้สึก
    if st.button("🚀 เริ่มการวิเคราะห์", type="primary"):
        start_time = time.time()
        
        # ทำการวิเคราะห์ความรู้สึก
        with st.spinner("🔍 กำลังวิเคราะห์ความรู้สึก..."):
            df_results = analyzer.analyze_sentiments(df, 'comment')
        
        # ทำการวิเคราะห์ข้อความ
        with st.spinner("📝 กำลังวิเคราะห์คุณสมบัติของข้อความ..."):
            df_analysis = analyze_text_features(df_results)
        
        analysis_time = time.time() - start_time
        st.success(f"✅ การวิเคราะห์เสร็จสิ้นใน {analysis_time:.2f} วินาที")
        
        # เก็บผลลัพธ์ใน session state
        st.session_state['df_results'] = df_analysis
        st.session_state['analysis_completed'] = True

    # แสดงผลลัพธ์หากการวิเคราะห์เสร็จสิ้น
    if st.session_state.get('analysis_completed', False):
        df_results = st.session_state['df_results']
        
        # สถิติ
        st.header("📈 ผลการวิเคราะห์")
        stats = calculate_sentiment_statistics(df_results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ความคิดเห็นทั้งหมด", len(df_results))
        with col2:
            st.metric("ความเชื่อมั่นเฉลี่ย", f"{stats['avg_confidence']:.2f}")
        with col3:
            st.metric("ความเชื่อมั่นสูง (%)", f"{stats['high_confidence_percentage']:.1f}%")
        
        # การกระจายความรู้สึก
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 การกระจายความรู้สึก")
            fig_hist = px.histogram(
                df_results, 
                x="sentiment", 
                color="sentiment",
                title="จำนวนความคิดเห็นแยกตามความรู้สึก"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("🎯 ความเชื่อมั่นตามความรู้สึก")
            fig_box = px.box(
                df_results, 
                x="sentiment", 
                y="confidence",
                title="การกระจายคะแนนความเชื่อมั่น"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # การวิเคราะห์ข้อความ
        st.subheader("📝 การวิเคราะห์ข้อความ")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_length = px.scatter(
                df_results.sample(min(500, len(df_results))), 
                x="text_length", 
                y="confidence", 
                color="sentiment",
                title="ความยาวข้อความ vs ความเชื่อมั่น"
            )
            st.plotly_chart(fig_length, use_container_width=True)
        
        with col2:
            emoji_sentiment = df_results.groupby(['sentiment', 'has_emoji']).size().reset_index(name='count')
            fig_emoji = px.bar(
                emoji_sentiment, 
                x="sentiment", 
                y="count", 
                color="has_emoji",
                title="การใช้อีโมจิตามความรู้สึก",
                barmode='group'
            )
            st.plotly_chart(fig_emoji, use_container_width=True)
        
        # ตัวอย่างผลลัพธ์
        st.subheader("📋 ตัวอย่างผลลัพธ์")
        display_cols = ['comment', 'sentiment', 'confidence', 'text_length', 'word_count']
        st.dataframe(
            df_results[display_cols].head(20),
            use_container_width=True
        )
        
        # ตัวเลือกการส่งออก
        st.subheader("⬇️ ส่งออกผลลัพธ์")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 ดาวน์โหลดผลลัพธ์ทั้งหมด (CSV)",
                csv_data,
                file_name=f"sentiment_analysis_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            summary_data = {
                'ความรู้สึก': list(stats['counts'].keys()),
                'จำนวน': list(stats['counts'].values()),
                'เปอร์เซ็นต์': list(stats['percentages'].values())
            }
            summary_df = pd.DataFrame(summary_data)
            summary_csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📊 ดาวน์โหลดสรุปผล (CSV)",
                summary_csv,
                file_name=f"sentiment_summary_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
