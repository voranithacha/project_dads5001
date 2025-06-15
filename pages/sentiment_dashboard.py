import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import plotly.express as px
import duckdb as db

st.title("🔍 Sentiment Analysis Dashboard (YouTube Comments)")

# === STEP 1: Load from DuckDB ===
con = db.connect('./comment.duckdb')
df = con.execute("SELECT comment_text_original as comment FROM yt_comment_full;").fetchdf()

if df.empty:
    st.error("❌ ไม่พบข้อมูลในฐานข้อมูล yt_comment_full")
    st.stop()

# === STEP 2: Load model ===
@st.cache_resource(show_spinner=True)
def load_model():
    model_name = "airesearch/wangchanberta-base-att-spm"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
    return tokenizer, model

tokenizer, model = load_model()

labels_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

# === STEP 3: Predict sentiment ===
def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    pred = torch.argmax(probs).item()
    return labels_map[pred]

with st.spinner("🔍 Analyzing sentiment..."):
    df["sentiment"] = df["comment"].astype(str).apply(predict_sentiment)

# === STEP 4: Show results ===
st.subheader("📋 ตัวอย่างผลลัพธ์ (Top 10)")
st.write(df[["comment", "sentiment"]].head(10))

# === STEP 5: Chart ===
st.subheader("📊 จำนวนความคิดเห็นแยกตามอารมณ์")
fig = px.histogram(df, x="sentiment", color="sentiment", barmode="group")
st.plotly_chart(fig)

# === STEP 6: Export ===
st.subheader("⬇️ ดาวน์โหลดผลลัพธ์")
st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="sentiment_result.csv")
