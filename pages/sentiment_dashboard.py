import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import plotly.express as px
import duckdb as db
import numpy as np
import re
from typing import List, Tuple, Dict
import time

st.set_page_config(page_title="แดชบอร์ดวิเคราะห์ความรู้สึก", layout="wide")
st.title("🔍 แดชบอร์ดวิเคราะห์ความรู้สึกขั้นสูง (ความคิดเห็น YouTube)")

# === โหลดโมเดลแบบแคช (อยู่นอกคลาสเท่านั้น) ===
@st.cache_resource(show_spinner=True)
def load_model(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
    return tokenizer, model

# === ตัววิเคราะห์ความรู้สึกแบบ Batch ===
class BatchSentimentAnalyzer:
    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.tokenizer, self.model = load_model(self.model_name)
        self.labels_map = {0: "เชิงลบ", 1: "เป็นกลาง", 2: "เชิงบวก"}

    def preprocess_text(self, text: str) -> str:
        if pd.isna(text) or not isinstance(text, str):
            return ""
        return re.sub(r'\s+', ' ', text.strip())[:512]

    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        clean_texts = [self.preprocess_text(t) for t in texts]
        inputs = self.tokenizer(clean_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            preds = torch.argmax(probs, dim=1)
            confs = torch.max(probs, dim=1)[0]

        return [(self.labels_map[p.item()], c.item()) for p, c in zip(preds, confs)]

    def analyze_sentiments(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        texts = df[text_column].tolist()
        total_batches = len(texts) // self.batch_size + (1 if len(texts) % self.batch_size else 0)
        all_sentiments, all_confidences = [], []

        progress = st.progress(0)
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            results = self.predict_batch(batch)
            for sent, conf in results:
                all_sentiments.append(sent)
                all_confidences.append(conf)
            progress.progress((i + self.batch_size) / len(texts))

        df_result = df.copy()
        df_result['sentiment'] = all_sentiments
        df_result['confidence'] = all_confidences
        return df_result

# === โหลดข้อมูลจาก DuckDB ===
@st.cache_data
def load_data_from_duckdb(db_path: str, table_name: str) -> pd.DataFrame:
    try:
        con = db.connect(db_path)
        tables_df = con.execute("SHOW TABLES;").fetchdf()
        if table_name not in tables_df['name'].values:
            st.error(f"❌ ไม่พบตาราง '{table_name}'")
            return pd.DataFrame()
        query = f"SELECT comment_text_original as comment FROM {table_name} LIMIT 1000;"
        df = con.execute(query).fetchdf()
        con.close()
        return df
    except Exception as e:
        st.error(f"❌ ข้อผิดพลาดฐานข้อมูล: {str(e)}")
        return pd.DataFrame()

# === วิเคราะห์ฟีเจอร์ข้อความ ===
def analyze_text_features(df: pd.DataFrame) -> pd.DataFrame:
    df['text_length'] = df['comment'].astype(str).str.len()
    df['word_count'] = df['comment'].astype(str).str.split().str.len()
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿⚠-⚡]')
    df['has_emoji'] = df['comment'].astype(str).str.contains(emoji_pattern, regex=True)
    df['emoji_count'] = df['comment'].astype(str).str.count(emoji_pattern)
    df['exclamation_count'] = df['comment'].astype(str).str.count('!')
    df['question_count'] = df['comment'].astype(str).str.count('?')
    return df

# === วิเคราะห์สถิติ ===
def calculate_sentiment_statistics(df: pd.DataFrame) -> Dict:
    stats = {
        'counts': df['sentiment'].value_counts().to_dict(),
        'percentages': (df['sentiment'].value_counts(normalize=True) * 100).round(2).to_dict(),
        'avg_confidence': df['confidence'].mean(),
        'high_confidence_count': len(df[df['confidence'] > 0.8]),
        'high_confidence_percentage': (len(df[df['confidence'] > 0.8]) / len(df)) * 100
    }
    return stats

# === Main ===
def main():
    st.sidebar.header("⚙️ การตั้งค่า")
    db_path = st.sidebar.text_input("🗂 เส้นทางฐานข้อมูล", "./comment.duckdb")
    table_name = st.sidebar.text_input("📄 ชื่อตาราง", "yt_comment_full")
    model_name = st.sidebar.selectbox("🧠 เลือกโมเดล", ["airesearch/wangchanberta-base-wiki", "cardiffnlp/twitter-roberta-base-sentiment-latest"])
    batch_size = st.sidebar.slider("🔢 ขนาดแบทช์", 8, 64, 32)

    df = load_data_from_duckdb(db_path, table_name)
    if df.empty:
        st.warning("⚠️ ไม่สามารถโหลดข้อมูลได้")
        return
    st.success(f"✅ โหลด {len(df)} ข้อความสำเร็จ")

    analyzer = BatchSentimentAnalyzer(model_name, batch_size)

    if st.button("🚀 เริ่มวิเคราะห์"):
        with st.spinner("กำลังวิเคราะห์..."):
            df_result = analyzer.analyze_sentiments(df, 'comment')
            df_result = analyze_text_features(df_result)

        stats = calculate_sentiment_statistics(df_result)
        st.metric("จำนวนความคิดเห็น", len(df_result))
        st.metric("ความเชื่อมั่นเฉลี่ย", f"{stats['avg_confidence']:.2f}")
        st.metric("ความคิดเห็นที่มั่นใจสูง", f"{stats['high_confidence_percentage']:.1f}%")

        st.subheader("📊 การกระจายความรู้สึก")
        fig1 = px.histogram(df_result, x="sentiment", color="sentiment", title="ความรู้สึก")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📋 ตัวอย่างข้อมูล")
        st.dataframe(df_result.head(10), use_container_width=True)

        st.subheader("⬇️ ดาวน์โหลด CSV")
        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button("📥 ดาวน์โหลดทั้งหมด", csv, "sentiment_results.csv", "text/csv")

if __name__ == "__main__":
    main()
