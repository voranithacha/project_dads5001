import streamlit as st
import duckdb as db

st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])

# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")
    con = db.connect('comment.duckdb')
    st.markdown("---")
    comment_type = st.selectbox("เลือกโมเดลรถ", ["BYD Atto3", "BYD Seal", "BYD Dolphin"])
    car_video_mapping = { "BYD Atto3": "OMV9F9zB4KU", "BYD Seal": "87lJCDADWCo", "BYD Dolphin": "CbkX7H-0BIU"}
    selected_video_id = car_video_mapping[comment_type]
    st.markdown("---")
    st.write("หมวด ราคา")



# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Random Forest, Neural Network, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Random Forest", "Neural Network"])
    st.write(f"คุณเลือกโมเดล: {model_type}")
