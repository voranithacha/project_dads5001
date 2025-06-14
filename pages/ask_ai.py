import streamlit as st
from auth.user_auth import login_or_register

# เรียกฟังก์ชันให้ login ก่อน
login_or_register()

st.title("🤖 Ask AI Chatbot")
st.write(f"ยินดีต้อนรับคุณ `{st.session_state['username']}`")

# เอา chatbot มาต่อ
