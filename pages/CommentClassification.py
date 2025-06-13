import streamlit as st
import duckdb as db
import pandas as pd # Import pandas to handle DataFrames

if con:
    st.subheader("ตรวจสอบข้อมูลทั้งหมดในตาราง (ชั่วคราว)")
    try:
        all_data = con.execute("SELECT * FROM comment_data LIMIT 10;").fetchdf()
        st.write(all_data)
    except db.Error as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลจากตาราง comment_data ได้: {e}")
        
st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])

# Establish connection to DuckDB
# Make sure 'comment.duckdb' exists and is in the same directory as your Streamlit app
con = None # Initialize connection to None
try:
    con = db.connect('comment.duckdb')
except Exception as e:
    st.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
    st.info("โปรดตรวจสอบว่าไฟล์ 'comment.duckdb' อยู่ในตำแหน่งที่ถูกต้องและไม่เสียหาย")

# --- Section 1: Preview Comments ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")

    if con: # Only proceed if connection is successful
        st.markdown("---")
        comment_type = st.selectbox("เลือกโมเดลรถ", ["BYD Atto3", "BYD Seal", "BYD Dolphin"])
        car_video_mapping = {
            "BYD Atto3": "OMV9F9zB4KU",
            "BYD Seal": "87lJCDADWCo",
            "BYD Dolphin": "CbkX7H-0BIU"
        }
        selected_video_id = car_video_mapping[comment_type]
        st.markdown("---")

        # Function to execute query and display results or a message
        def display_comments(title, keywords, video_id, connection):
            st.write(f"**หมวด {title}**")
            query = f"""
            SELECT DISTINCT comment
            FROM comment_data
            WHERE video_id = '{video_id}'
            AND ({' OR '.join([f"comment LIKE '%{k}%'" for k in keywords])})
            ORDER BY RANDOM() -- Orders randomly to get different top 5 each time if no specific ranking
            LIMIT 5;
            """
            try:
                df = connection.execute(query).fetchdf()
                if not df.empty:
                    st.dataframe(df, hide_index=True) # Using st.dataframe for better display
                else:
                    st.info(f"🚫 ไม่พบคอมเมนต์ในหมวด '{title}' สำหรับ {comment_type}")
            except db.Error as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลหมวด '{title}': {e}")
                st.warning(f"โปรดตรวจสอบว่าตาราง 'comment_data' มีอยู่จริงและมีข้อมูลที่ตรงกับเงื่อนไขสำหรับ {comment_type} หรือไม่")
            st.markdown("---")

        # Define keywords for each category
        price_keywords = ['ราคา', 'ซื้อ', 'ขาย', 'ถูก', 'แพง']
        efficient_keywords = ['คุณภาพ', 'อะไหล่', 'พลังงาน', 'ถี่', 'ทน']
        tech_keywords = ['ปลอด', 'ระบบ', 'แจ้งเตือน', 'ชาร์จ', 'แบต']
        design_keywords = ['สวย', 'สี', 'ข้างใน', 'หน้า', 'ดีไซน์']

        # Display comments for each category
        display_comments("ราคา", price_keywords, selected_video_id, con)
        display_comments("ประสิทธิภาพ", efficient_keywords, selected_video_id, con)
        display_comments("เทคโนโลยี", tech_keywords, selected_video_id, con)
        display_comments("รูปร่าง", design_keywords, selected_video_id, con)

# --- Section 2: ML Modeling ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Random Forest, Neural Network, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Random Forest", "Neural Network"])
    st.write(f"คุณเลือกโมเดล: {model_type}")

