import streamlit as st
import duckdb as db

st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])

# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    # ดึงคอมเมนต์จาก MongoDB หรือ CSV แล้วโชว์
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")

    con = db.connect('comment.duckdb')
    result = con.execute(f"""SELECT * FROM comment_data""")
    st.write(result)
    st.write("test1")
    car_video_mapping = { "BYD Atto3": "OMV9F9zB4KU", "BYD Seal": "87lJCDADWCo", "BYD Dolphin": "CbkX7H-0BIU"}
    st.write("test2")
    selected_video_id = car_video_mapping[comment_type]
    st.write("test3")
    st.write("หมวด ราคา")
    price = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%ราคา%' or comment like '%ซื้อ%' or comment like '%ขาย%' or comment like '%ถูก%' or comment like '%แพง%')
    --and (comment like '%ราคา%' or comment like '%ซื้อ%' or comment like '%ขาย%' or comment like '%ถูก%' or comment like '%แพง%' or comment like '%ลด%' or comment like '%บาท%' or comment like '%ล้าน%' or comment like '%แสน%' or comment like '%เงิน%')
    limit 5; 
    """)
    st.write(price)

    st.write("หมวด ประสิทธิภาพ")
    efficient = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%คุณภาพ%' or comment like '%อะไหล่%' or comment like '%พลังงาน%' or comment like '%ถี่%' or comment like '%ทน%')
    --and (comment like '%เสียง%' or comment like '%ขับขี่%' or comment like '%พลังงาน%' or comment like '%ถี่%' or comment like '%ทน%' or comment like '%คุณภาพ%' or comment like '%อะไหล่%')
    limit 5; 
    """)
    st.write(efficient)

    st.write("หมวด เทคโนโลยี")
    tech = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%ปลอด%' or comment like '%ระบบ%' or comment like '%แจ้งเตือน%' or comment like '%ชาร์จ%' or comment like '%แบต%')
    --and (comment like '%ปลอด%' or comment like '%ระบบ%' or comment like '%แจ้งเตือน%' or comment like '%ชาร์จ%' or comment like '%กล้อง%' or comment like '%แบต%' or comment like '%ช่วย%' or comment like '%เทค%' or comment like '%ออฟชั่น%' or comment like '%ไฟฟ้า%')
    limit 5; 
    """)
    st.write(tech)

    st.write("หมวด รูปร่าง")
    design = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%สวย%' or comment like '%สี%' or comment like '%ข้างใน%' or comment like '%หน้า%' or comment like '%ดีไซน์%')
    --and (comment like '%สวย%' or comment like '%สี%' or comment like '%ภาย%' or comment like '%ข้างใน%' or comment like '%ทรง%' or comment like '%รูป%' or comment like '%หน้า%' or comment like '%หรู%' or comment like '%หรา%' or comment like '%นอก%' or comment like '%งาม%' or comment like '%ดีไซน์%')
    limit 5; 
    """)
    st.write(design)


# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Random Forest, Neural Network, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Random Forest", "Neural Network"])
    st.write(f"คุณเลือกโมเดล: {model_type}")



