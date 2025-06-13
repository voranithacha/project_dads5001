import streamlit as st
import duckdb as db
st.write("test")
st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])
st.write("test")
# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")
    st.write("test")
    con = db.connect('comment.duckdb')
    if 'con' not in st.session_state:
      st.session_state.con = db.connect('comment.duckdb')
    con = st.session_state.con
    df = con.execute("SELECT * FROM comment_data").fetchdf()
    st.write("📄 แสดงตัวอย่างข้อมูลจากฐานข้อมูล:")
    st.write(df.head())

# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Random Forest, Neural Network, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Random Forest", "Neural Network"])
    st.write(f"คุณเลือกโมเดล: {model_type}")
