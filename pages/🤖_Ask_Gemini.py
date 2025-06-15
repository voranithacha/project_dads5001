import streamlit as st
import pandas as pd
import io
import json
from google import genai

from auth.user_auth import login_or_register  # เรียกระบบล๊อกอิน

# === ตรวจสิทธิ์ก่อนเข้าถึง ===
login_or_register()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# === หากยังไม่ล็อกอิน ให้แสดงหน้า login/register ===
if not st.session_state["logged_in"]:
    st.title("🔐 กรุณาเข้าสู่ระบบเพื่อใช้งาน Ask AI")

    tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "สมัครสมาชิก"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("เข้าสู่ระบบ"):
            if login_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("✅ เข้าสู่ระบบสำเร็จ")
                st.experimental_rerun()
            else:
                st.error("❌ Username หรือ Password ไม่ถูกต้อง")

    with tab2:
        new_user = st.text_input("ตั้ง Username", key="reg_user")
        new_pass = st.text_input("ตั้ง Password", type="password", key="reg_pass")
        if st.button("ลงทะเบียน"):
            if register_user(new_user, new_pass):
                st.success("✅ สมัครสมาชิกสำเร็จ! โปรดเข้าสู่ระบบ")
            else:
                st.error("⚠️ Username นี้ถูกใช้แล้ว")

    st.stop()

# === ถ้าล็อกอินแล้ว แสดงเนื้อหาหลักของ Ask AI ===
st.title("🤖 ยินดีต้อนรับสู่ Ask AI")
st.write(f"คุณล็อกอินในชื่อ: `{st.session_state['username']}`")

if st.button("ออกจากระบบ"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.experimental_rerun()

# === ตัวแปร และ Key ===
CSV_PATH = './data/youtube_comments_full.csv'
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# === ฟังก์ชันช่วย ===
def convert_bytes_to_dataframe(byte_data, encoding='utf-8', **kwargs):
    try:
        string_data = byte_data.decode(encoding)
        data_io = io.StringIO(string_data)
        df = pd.read_csv(data_io, **kwargs)
        return df
    except UnicodeDecodeError as e:
        st.error(f"Decoding error: {e}")
        return None
    except pd.errors.EmptyDataError:
        st.error("Empty data error: The uploaded file is empty.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def format_dict_as_text(data_list):
    formatted_rows = ["\n".join([f"{k}: {v}" for k, v in row.items()]) for row in data_list]
    return "\n\n".join(formatted_rows)

def ask_gemini_about_data(client, model, df_dict, question):
    context_text = format_dict_as_text(df_dict[:50])  # จำกัดข้อมูล 50 records เพื่อความเร็ว
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

# === Sidebar History ===
with st.sidebar:
    st.subheader("📜 Conversations History")
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    if st.session_state.qa_history:
        for i, item in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
            st.markdown(f"**{i}. คำถาม:** {item['question']}")
            st.markdown(f"✍️ คำตอบ: {item['answer'][:150]}...")
            st.markdown("---")
        if st.button("🗑️ Clear Conversations History"):
            st.session_state.qa_history = []
    else:
        st.info("No Conversations History")

# === เลือกแหล่งข้อมูล ===
st.subheader("📊 เลือกแหล่งข้อมูลความคิดเห็น")

data_source = st.radio(
    "เลือกแหล่งข้อมูล CSV",
    ["📁 Default CSV (ระบบ)", "📤 Upload CSV File จากเครื่อง"]
)

df = None
df_dict = None

if data_source == "📁 Default CSV (ระบบ)":
    try:
        df = pd.read_csv(CSV_PATH)
        st.success(f"โหลดข้อมูลจาก `{CSV_PATH}` สำเร็จ!")
        st.write(df)
        df_dict = df.to_dict(orient='records')
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")

elif data_source == "📤 Upload CSV File จากเครื่อง":
    uf_csv = st.file_uploader("📂 Upload CSV File", type=["csv"])
    if uf_csv is not None:
        bytes_data = uf_csv.getvalue()
        df = convert_bytes_to_dataframe(bytes_data, delimiter=',')
        if df is not None:
            st.success("✅ อัปโหลดและอ่านไฟล์ CSV สำเร็จ")
            st.write(df)
            df_dict = df.to_dict(orient='records')

# === ถ้ามีข้อมูล ให้ถาม Gemini ได้ ===
if df_dict:
    st.subheader("🧠 Ask Questions about the Data")

    user_question = st.text_input("Enter your question:❓")
    if st.button("Ask Gemini") and user_question:
        answer = ask_gemini_about_data(client, "gemini-2.0-flash", df_dict, user_question)
        st.write("📌 **Answer:**")
        st.success(answer)

        # Save to history
        st.session_state.qa_history.append({
            "question": user_question,
            "answer": answer
        })

    # === Export Options ===
    st.markdown("### 📤 Export Options")
    # CSV
    csv_data = pd.DataFrame(df_dict).to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="comments_data.csv",
        mime="text/csv"
    )

 
