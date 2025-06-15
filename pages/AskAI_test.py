import streamlit as st
import pandas as pd
import io
import json
from google import genai
import os

# import ฟังก์ชันจาก comment_fetcher.py
from comment_fetcher import get_all_comments

#------- YouTube API key และ Video IDs
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

VIDEO_IDS = ["OMV9F9zB4KU", "87lJCDADWCo", "CbkX7H-0BIU"]
CSV_PATH = './data/youtube_comments_full.csv'  # default CSV

# === (ระบบล็อกอินของคุณเดิม) ===
from auth.user_auth import login_or_register
login_or_register()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    # ... (code login/register เดิม)
    st.stop()

st.title("🤖 ยินดีต้อนรับสู่ Ask AI")
st.write(f"คุณล็อกอินในชื่อ: `{st.session_state['username']}`")
if st.button("ออกจากระบบ"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.experimental_rerun()

# --- Section: เลือกแหล่งข้อมูลความคิดเห็น ---
st.header("⚙️ เลือกแหล่งข้อมูลความคิดเห็น")

data_source = st.radio(
    "เลือกแหล่งข้อมูลความคิดเห็น",
    options=[
        "โหลดจากไฟล์ CSV ล่าสุด (ดึงข้อมูลใหม่จาก YouTube)",
        "อัปโหลดไฟล์ CSV จากเครื่องของคุณ",
        "ใช้ข้อมูลจากไฟล์ CSV เริ่มต้น"
    ]
)

df = None
df_dict = None

if data_source == "โหลดจากไฟล์ CSV ล่าสุด (ดึงข้อมูลใหม่จาก YouTube)":
    if st.button("📥 ดึงข้อมูลความคิดเห็นล่าสุดและบันทึกเป็น CSV"):
        with st.spinner("กำลังดึงข้อมูล... โปรดรอสักครู่"):
            df = get_all_comments(VIDEO_IDS, YOUTUBE_API_KEY)
            st.success(f"ดึงข้อมูลเสร็จสิ้น จำนวน {len(df)} ความคิดเห็น")
    # โหลดไฟล์ CSV ที่ดึงมาแล้ว (ถ้ามี)
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.write("ตัวอย่างข้อมูลที่โหลดจาก CSV ล่าสุด:")
        st.dataframe(df.head())
    else:
        st.info("ยังไม่มีไฟล์ CSV ล่าสุด กรุณากดปุ่มด้านบนเพื่อดึงข้อมูล")

elif data_source == "อัปโหลดไฟล์ CSV จากเครื่องของคุณ":
    uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ CSV ความคิดเห็น", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("ตัวอย่างข้อมูลที่อัปโหลด:")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

elif data_source == "ใช้ข้อมูลจากไฟล์ CSV เริ่มต้น":
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.write("ตัวอย่างข้อมูลจากไฟล์ CSV เริ่มต้น:")
        st.dataframe(df.head())
    else:
        st.warning(f"ไม่พบไฟล์ CSV เริ่มต้นที่ {CSV_PATH}")

# แปลง DataFrame เป็น dict สำหรับส่งให้ AI
if df is not None:
    df_dict = df.to_dict(orient='records')

# === เริ่มระบบ AI ถ้ามีข้อมูล ===

client = genai.Client(api_key=GEMINI_API_KEY)

def format_dict_as_text(data_list):
    formatted_rows = ["\n".join([f"{k}: {v}" for k, v in row.items()]) for row in data_list]
    return "\n\n".join(formatted_rows)

def ask_gemini_about_data(client, model, df_dict, question):
    context_text = format_dict_as_text(df_dict[:50])  # limit ตัวอย่างข้อมูล 50 rows เพื่อประสิทธิภาพ
    prompt = (
        "You are a data analyst. Here's a sample of the data:\n\n"
        f"{context_text}\n\n"
        f"Now answer this question based on the data:\n{question}"
    )
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

if df_dict:
    st.subheader("🧠 ถามคำถามเกี่ยวกับข้อมูล")

    user_question = st.text_input("พิมพ์คำถามของคุณที่นี่:")
    if st.button("ถาม Gemini") and user_question.strip():
        with st.spinner("กำลังประมวลผลคำตอบ..."):
            answer = ask_gemini_about_data(client, "gemini-2.0-flash", df_dict, user_question)
        st.success("📌 คำตอบ:")
        st.write(answer)

        # เก็บประวัติถาม-ตอบ
        if "qa_history" not in st.session_state:
            st.session_state.qa_history = []
        st.session_state.qa_history.append({
            "question": user_question,
            "answer": answer
        })

# แสดงประวัติการถามตอบใน Sidebar
with st.sidebar:
    st.subheader("📜 ประวัติการสนทนา")
    if "qa_history" in st.session_state and st.session_state.qa_history:
        for i, item in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
            st.markdown(f"**{i}. คำถาม:** {item['question']}")
            st.markdown(f"✍️ คำตอบ: {item['answer'][:150]}...")
            st.markdown("---")
        if st.button("🗑️ ล้างประวัติการสนทนา"):
            st.session_state.qa_history = []
    else:
        st.info("ยังไม่มีประวัติการสนทนา")

# Export ตัวเลือกดาวน์โหลดข้อมูล
if df_dict:
    st.markdown("### 📤 ตัวเลือกดาวน์โหลดข้อมูล")

    json_data = json.dumps(df_dict, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇️ ดาวน์โหลด JSON",
        data=json_data,
        file_name="comments_data.json",
        mime="application/json"
    )

    csv_data = pd.DataFrame(df_dict).to_csv(index=False)
    st.download_button(
        label="⬇️ ดาวน์โหลด CSV",
        data=csv_data,
        file_name="comments_data.csv",
        mime="text/csv"
    )

    excel_buffer = io.BytesIO()
    pd.DataFrame(df_dict).to_excel(excel_buffer, index=False, engine='xlsxwriter')
    st.download_button(
        label="⬇️ ดาวน์โหลด Excel",
        data=excel_buffer,
        file_name="comments_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

