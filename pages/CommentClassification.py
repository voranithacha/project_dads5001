import streamlit as st
import duckdb as db

st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])

# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")
    # comment_type = st.selectbox("เลือกโมเดลรถ", ["BYD Atto3", "BYD Seal", "BYD Dolphin"])
    # car_video_mapping = { "BYD Atto3": "OMV9F9zB4KU", "BYD Seal": "87lJCDADWCo", "BYD Dolphin": "CbkX7H-0BIU"}
    # selected_video_id = car_video_mapping[comment_type]
    st.markdown("---")
    st.write("หมวด ราคา")
    con = db.connect('comment.duckdb')
    price = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id =  'OMV9F9zB4KU' -- '{selected_video_id}'
    and (comment like '%ราคา%' or comment like '%ซื้อ%' or comment like '%ขาย%' or comment like '%ถูก%' or comment like '%แพง%')
    limit 5; """).fetchdf()
    st.write(price)
    st.markdown("---")
    st.write("หมวด ประสิทธิภาพ")
    efficient = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%คุณภาพ%' or comment like '%อะไหล่%' or comment like '%พลังงาน%' or comment like '%ถี่%' or comment like '%ทน%')
    limit 5; """).fetchdf()
    st.write(efficient)
    st.markdown("---")
    st.write("หมวด เทคโนโลยี")
    tech = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%ปลอด%' or comment like '%ระบบ%' or comment like '%แจ้งเตือน%' or comment like '%ชาร์จ%' or comment like '%แบต%')
    limit 5; """).fetchdf()
    st.write(tech)
    st.markdown("---")
    st.write("หมวด รูปร่าง")
    design = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%สวย%' or comment like '%สี%' or comment like '%ข้างใน%' or comment like '%หน้า%' or comment like '%ดีไซน์%')
    limit 5; """).fetchdf()
    st.write(design)


# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Random Forest, Neural Network, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Random Forest", "Neural Network"])
    st.write(f"คุณเลือกโมเดล: {model_type}")
