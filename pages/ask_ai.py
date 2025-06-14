import streamlit as st
from auth.user_auth import login_or_register

st.set_page_config(page_title="Ask AI")

# เรียก login/register ถ้ายังไม่ได้เข้าสู่ระบบ
login_or_register()

# หากผ่าน login แล้วจะมาถึงส่วนนี้
st.title("🤖 ยินดีต้อนรับสู่ Ask AI")
st.write(f"คุณล็อกอินในชื่อ: `{st.session_state['username']}`")

if st.button("ออกจากระบบ"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.experimental_rerun()

# 🔽 ส่วนของ AI Chatbot หรือฟีเจอร์อื่น ๆ ด้านล่างนี้
st.write("🔍 พิมพ์คำถามของคุณด้านล่างเพื่อให้ AI ช่วยตอบ...")
