import streamlit as st
import pandas as pd
import plotly.express as px
import torch
import duckdb as db
import re
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification

st.set_page_config(page_title="แดชบอร์ดวิเคราะห์ความรู้สึก", layout="wide")
st.title("🔍 แดชบอร์ดวิเคราะห์ความรู้สึกจากความคิดเห็น YouTube")

# ✅ ย้ายออกมานอกคลาส แล้วใช้ cache
@st.cache_resource(show_spinner=True)
def load_model(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
    return tokenizer, model

@st.cache_data
def load_data(db_path: str, table_name: str) -> pd.DataFrame:
    try:
        con = db.connect(db_path)
        query = f"SELECT comment_text_original as comment FROM {table_name} LIMIT 1000;"
        df = con.execute(query).fetchdf()
        con.close()
        return df
    except Exception as e:
        st.error(f"❌ ไม่สามารถโหลดข้อมูลจาก DuckDB ได้: {e}")
        return pd.DataFrame()

def predict_sentiments(df, tokenizer, model, batch_size: int = 32):
    labels_map = {0: "เชิงลบ", 1: "เป็นกลาง", 2: "เชิงบวก"}
    comments = df["comment"].astype(str).tolist()

    sentiments, confidences = [], []
    total = len(comments)
    progress_bar = st.progress(0)
    status = st.empty()

    for i in range(0, total, batch_size):
        batch = comments[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
            preds = torch.argmax(probs, dim=1)
            confs = torch.max(probs, dim=1)[0]
        sentiments.extend([labels_map[p.item()] for p in preds])
        confidences.extend([c.item() for c in confs])
        progress_bar.progress(min((i + batch_size) / total, 1.0))
        status.text(f"วิเคราะห์ {min(i + batch_size, total)} / {total} ความคิดเห็น")

    df["sentiment"] = sentiments
    df["confidence"] = confidences
    progress_bar.empty()
    status.empty()
    return df

def main():
    st.sidebar.header("⚙️ การตั้งค่า")
    db_path = st.sidebar.text_input("📁 ที่อยู่ฐานข้อมูล DuckDB", "./comment.duckdb")
    table_name = st.sidebar.text_input("🧾 ชื่อตาราง", "yt_comment_full")
    model_name = st.sidebar.selectbox("🤖 เลือกโมเดล", [
        "airesearch/wangchanberta-base-att-spm",
        "airesearch/wangchanberta-base-wiki"
    ])
    batch_size = st.sidebar.slider("📦 Batch size", 8, 64, 32)

    df = load_data(db_path, table_name)
    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูลในตารางที่ระบุ")
        st.stop()

    st.success(f"✅ โหลดข้อมูลจำนวน {len(df)} ความคิดเห็นเรียบร้อยแล้ว")

    if st.button("🚀 เริ่มวิเคราะห์ความคิดเห็น"):
        with st.spinner("📊 กำลังโหลดโมเดล..."):
            tokenizer, model = load_model(model_name)

        with st.spinner("🔍 กำลังวิเคราะห์..."):
            start = time.time()
            df_result = predict_sentiments(df, tokenizer, model, batch_size)
            duration = time.time() - start
        st.success(f"✅ วิเคราะห์เสร็จใน {duration:.2f} วินาที")

        st.subheader("📈 สรุปผลความรู้สึก")
        fig = px.histogram(df_result, x="sentiment", color="sentiment", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📝 ตัวอย่างผลลัพธ์")
        st.dataframe(df_result[["comment", "sentiment", "confidence"]].head(20))

        st.subheader("⬇️ ดาวน์โหลดไฟล์ผลลัพธ์")
        csv = df_result.to_csv(index=False).encode("utf-8")
        st.download_button("📄 ดาวน์โหลด CSV", csv, file_name="sentiment_results.csv", mime="text/csv")

if __name__ == "__main__":
    main()
