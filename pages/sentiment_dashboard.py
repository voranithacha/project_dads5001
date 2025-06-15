import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import plotly.express as px
import duckdb as db

st.title("🔍 Thai Sentiment Analysis Dashboard (YouTube Comments)")

# === STEP 1: Load comments from DuckDB ===
con = db.connect('./comment.duckdb')
df = con.execute("SELECT comment_text_original as comment FROM yt_comment_full;").fetchdf()

if df.empty:
    st.error("❌ ไม่พบข้อมูลในตาราง yt_comment_full")
    st.stop()

# === STEP 2: Load Thai Sentiment Model ===
@st.cache_resource(show_spinner=True)
def load_model():
    model_name = "VISTEC/bert-base-thai-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
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

with st.spinner("🔍 วิเคราะห์อารมณ์จากความคิดเห็น..."):
    df["sentiment"] = df["comment"].astype(str).apply(predict_sentiment)

# === STEP 4: Show results ===
st.subheader("📋 ตัวอย่างผลลัพธ์ (Top 10)")
st.dataframe(df[["comment", "sentiment"]].head(10), use_container_width=True)

# === STEP 5: Chart ===
st.subheader("📊 จำนวนความคิดเห็นแยกตามอารมณ์")
fig = px.histogram(df, x="sentiment", color="sentiment", barmode="group")
st.plotly_chart(fig, use_container_width=True)

# === STEP 6: Export ===
st.subheader("⬇️ ดาวน์โหลดผลลัพธ์")
st.download_button("📥 Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="thai_sentiment_results.csv")
