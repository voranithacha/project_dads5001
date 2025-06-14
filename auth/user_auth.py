import streamlit as st
from pymongo import MongoClient
import hashlib

def get_db():
    client = MongoClient(st.secrets["MONGO_URI"])
    db = client["user_db"]
    return db["users"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = get_db()
    st.write("📡 เชื่อมต่อ MongoDB สำเร็จ")
    if users.find_one({"username": username}):
        return False
    users.insert_one({
        "username": username,
        "password": hash_password(password)
    })
    st.success("✅ บันทึกข้อมูลลง MongoDB แล้ว")
    return True

def login_user(username, password):
    users = get_db()
    user = users.find_one({"username": username})
    return user and user["password"] == hash_password(password)

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
            if st.button("ลงทะเบียน", key="register_button"):
                st.write("🚀 ปุ่มลงทะเบียนถูกกดแล้ว")
                if register_user(new_user, new_pass):
                    st.success("✅ สมัครสมาชิกสำเร็จ! โปรดเข้าสู่ระบบ")
                else:
                    st.error("⚠️ Username นี้ถูกใช้แล้ว")

        st.stop()
