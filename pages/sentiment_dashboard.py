import streamlit as st
import pandas as pd
import re
import time
import duckdb as db
from typing import List, Tuple, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import plotly.express as px

st.set_page_config(page_title="แดชบอร์ดวิเคราะห์ความรู้สึก", layout="wide")
st.title("🔍 แดชบอร์ดวิเคราะห์ความรู้สึกขั้นสูง (ความคิดเห็น YouTube)")

# === คลาสวิเคราะห์ความรู้สึก ===
class BatchSentimentAnalyzer:
    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
        self.labels_map = {0: "เชิงลบ", 1: "เป็นกลาง", 2: "เชิงบวก"}

    def preprocess_text(self, text: str) -> str:
        if pd.isna(text) or not isinstance(text, str):
            return ""
        return re.sub(r'\s+', ' ', text.strip())[:512]

    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        clean_texts = [self.preprocess_text(text) for text in texts]
        inputs = self.tokenizer(clean_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            preds = torch.argmax(probs, dim=1)
            confidences = torch.max(probs, dim=1)[0]
        return [(self.labels_map[p.item()], c.item()) for p, c in zip(preds, confidences)]

    def analyze_sentiments(self, df: pd.DataFrame, text_col: str) -> pd.DataFrame:
        texts = df[text_col].tolist()
        sentiments, confidences = [], []
        progress_bar = st.progress(0)
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_results = self.predict_batch(batch)
            for s, c in batch_results:
                sentiments.append(s)
                confidences.append(c)
            progress_bar.progress((i + self.batch_size) / len(texts))
        progress_bar.empty()
        df = df.copy()
        df["sentiment"] = sentiments
        df["confidence"] = confidences
        return df

# ✅ ใช้ cache ที่ถูกต้องกับฟังก์ชัน
@st.cache_resource
def load_analyzer(model_name: str, batch_size: int = 32):
    return BatchSentimentAnalyzer(model_name, batch_size)

@st.cache_data
def load_data(db_path: str, table: str) -> pd.DataFrame:
    try:
        con = db.connect(db_path)
        df = con.execute(f"SELECT comment_text_original AS comment FROM {table} LIMIT 1000;").fetchdf()
        con.close()
        return df
    except Exception as e:
        st.error(f"❌ ไม่สามารถโหลดข้อมูลได้: {e}")
        return pd.DataFrame()

def main():
    st.sidebar.header("⚙️ ตั้งค่า")
    db_path = st.sidebar.text_input("📂 เส้นทางฐานข้อมูล", value="./comment.duckdb")
    table_name = st.sidebar.text_input("🗃️ ชื่อตาราง", value="yt_comment_full")
    batch_size = st.sidebar.slider("📦 Batch Size", 8, 64, 32)
    model_name = st.sidebar.selectbox("🤖 เลือกโมเดล", [
        "airesearch/wangchanberta-base-wiki", 
        "cardiffnlp/twitter-roberta-base-sentiment-latest"
    ])

    df = load_data(db_path, table_name)

    if df.empty:
        st.warning("ไม่พบข้อมูล")
        return

    st.success(f"✅ โหลด {len(df)} ความคิดเห็นสำเร็จ")

    if st.button("🚀 เริ่มการวิเคราะห์"):
        analyzer = load_analyzer(model_name, batch_size)
        with st.spinner("🔍 กำลังวิเคราะห์..."):
            df = analyzer.analyze_sentiments(df, "comment")

        st.session_state["df"] = df
        st.session_state["done"] = True

    if st.session_state.get("done", False):
        df = st.session_state["df"]
        st.subheader("📊 ผลการวิเคราะห์")
        st.dataframe(df.head(20))

        fig = px.histogram(df, x="sentiment", color="sentiment", title="ความรู้สึกของความคิดเห็น")
        st.plotly_chart(fig)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ ดาวน์โหลดผลลัพธ์", csv, "sentiment_results.csv", "text/csv")

if __name__ == "__main__":
    main()
