import json
import os
import hashlib
import streamlit as st

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

# ส่วนนี้คือ UI สำหรับ login/register
def login_or_register():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if not st.session_state["logged_in"]:
        st.title("🔐 เข้าสู่ระบบเพื่อใช้งาน Ask AI")

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
