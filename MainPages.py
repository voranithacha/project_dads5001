import streamlit as st
from collections import Counter
import pandas as pd
from pymongo import MongoClient
import json

#for word clound
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords
import re

st.title("YouTube Comments Analysis")
st.markdown("""
### 🔰 Introduction
This project is an extension of the DADS5002 course, focusing on text classification using machine learning techniques. The objective is to automatically categorize comments extracted from YouTube videos into predefined classifications, helping to uncover insights from user feedback.
"""
"""### 🔍 Data Source and Collection
Text Comments: Collected from YouTube comment sections of car review videos.
Target Brand: BYD, specifically its top 3 best-selling models in the Thai market — Atto 3, Seal, and Dolphin.
YouTube Channel: Data was gathered from the autolifethailand official channel, which has over 1.06 million subscribers and is known for its trusted automotive content.
The dataset consists of comments from three BYD-related car review clips, which serve as the foundation for building and evaluating the classification model.
"""
"""### 💡 AI-Powered Insight Assistant
To enhance the value of this project, an AI-powered assistant feature is integrated for premium users, enabling interactive exploration of classified comments. This assistant helps identify key highlights, detect emerging themes, and provide contextual insight summaries, supporting faster and smarter decision-making based on public sentiment.
""")

# === YouTube Video IDs ===
video_ids = ["OMV9F9zB4KU", "87lJCDADWCo", "CbkX7H-0BIU"]
# === Show Videos ===
st.subheader("▶️ Video Reference 🔴")
col1, col2, col3 = st.columns(3)
with col1:
    st.video(f"https://www.youtube.com/watch?v={video_ids[0]}")
    st.caption("BYD Atto3")
with col2:
    st.video(f"https://www.youtube.com/watch?v={video_ids[1]}")
    st.caption("BYD Seal")
with col3:
    st.video(f"https://www.youtube.com/watch?v={video_ids[2]}")
    st.caption("BYD Dolphin")
# === Sidebar: Conversation History ===

# === MongoDB ===
mongo_uri = "mongodb+srv://readwrite:OSbtDM3XE8nP2JqT@voranitha.z6voe4w.mongodb.net/"
 
@st.cache_resource
def get_database():
    """
    เชื่อมต่อกับ MongoDB Atlas และส่งคืน object ของ database
    ใช้ st.cache_resource เพื่อให้เชื่อมต่อเพียงครั้งเดียวเมื่อแอปพลิเคชันเริ่มทำงาน
    """
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping') # ทดสอบการเชื่อมต่อ
        return client.car # คืน database 'car'
    except ConnectionFailure as e:
        st.error(f"ไม่สามารถเชื่อมต่อกับ MongoDB ได้: {e}")
        st.stop() # หยุดการทำงานของ Streamlit หากเชื่อมต่อไม่ได้
    except OperationFailure as e:
        st.error(f"เกิดข้อผิดพลาดในการดำเนินงาน MongoDB: {e}")
        st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        st.stop()
 
# --- เริ่มต้น Streamlit App ---
 
# ดึง database object
db = get_database()
collection = db.comment
data = list(collection.find())  # Get all documents as a list of dicts
df = pd.DataFrame(data)         # Convert to DataFrame

# ดึงข้อมูลเฉพาะ video_title
#comments = list(collection.find({}, {"video_title": 1}))
#comments = list(collection.find({}, {"_id": 0, "video_title": 1}))

# แปลงเป็น DataFrame
#df = pd.DataFrame(comments)
#st.write(comments[:5]) 

# ตรวจสอบคอลัมน์
if 'video_title' not in df.columns:
    st.error("ไม่พบคอลัมน์ 'video_title'")
else:
    # นับจำนวนความคิดเห็นต่อ video_title
    video_counts = df['video_title'].value_counts().reset_index()
    video_counts.columns = ['video_title', 'count']

    # ฟังก์ชันสร้าง label อัตโนมัติ
    def generate_label(title):
        title_upper = title.upper()
        if "ATTO" in title_upper:
            return "BYD Atto3"
        elif "SEAL" in title_upper:
            return "BYD Seal"
        elif "DOLPHIN" in title_upper:
            return "BYD Dolphin"
        else:
            return "อื่น ๆ"

    # สร้างคอลัมน์ label
    video_counts['Model'] = video_counts['video_title'].apply(generate_label)

    # เรียงคอลัมน์ใหม่
    result_df = video_counts[['Model', 'video_title', 'count']]

    # แสดงผล
    st.subheader("📊 Video Comment Counts")
    st.dataframe(result_df)

# Word Cloud
comments_collection = db.comment

# --- สร้าง Word Cloud ---
# --- กำหนด Mapping ชื่อ Model กับ Keyword ใน title ---
model_keywords = {
    "BYD Atto3": "ATTO",
    "BYD Dolphin": "DOLPHIN",
    "BYD Seal": "SEAL"
}

# --- สร้าง Dropdown ให้ผู้ใช้เลือก Model ---
selected_model = st.selectbox("เลือกรุ่นรถยนต์ที่ต้องการดู Word Cloud", list(model_keywords.keys()))

if selected_model and st.button("สร้าง Word Cloud"):
    try:
        keyword = model_keywords[selected_model]

        # Query เฉพาะคอมเมนต์ที่ title มีคีย์เวิร์ดของรุ่นที่เลือก
        cursor = comments_collection.find(
            {"video_title": {"$regex": keyword, "$options": "i"}},
            {"comment": 1}
        )

        # ดึงและทำความสะอาดข้อความ
        comments = [re.sub(r"[^\u0E00-\u0E7F]+", " ", doc.get("comment", "")) for doc in cursor]
        full_text = " ".join(comments)

        # ตัดคำและกรอง Stopwords
        tokens = word_tokenize(full_text, engine="newmm")
        stopwords = set(thai_stopwords()).union({"ครับ", "ค่ะ", "ๆ", "นะ", "เลย","า","ด","น"})
        temp_filtered_tokens = [w for w in tokens if w not in custom_stopwords and len(w) > 1]
        allowed_words = {"ดี", "แรง", "ประหยัด", "สวย", "น่ารัก", "ราคา", "คุ้ม", "สบาย", "เร็ว", "เงียบ","ราคา","ซื้อ","ขาย","ถูก","แพง","ลด","บาท","ล้าน","แสน","เงิน","เสียง","ขับขี่","พลังงาน","ถี่","ทน","คุณภาพ","อะไหล่","ปลอด","ระบบ","แจ้งเตือน","ชาร์จ","กล้อง","แบต","ช่วย","เทค","ออฟชั่น","ไฟฟ้า","สวย","สี","ภาย","ข้างใน","ทรง","รูป","หน้า","หรู","หรา","นอก","งาม","ดีไซน์"}
        filtered = [w for w in tokens if w not in stopwords and len(w) > 1]

        # สร้าง Word Cloud
        wordcloud = WordCloud(
            font_path="fonts/THSarabunNew.ttf",
            width=800,
            height=400,
            background_color="white",
            collocations=False
        ).generate(" ".join(filtered))

        # แสดงผล
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
        st.success(f"แสดง Word Cloud สำหรับ: {selected_model}")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้าง Word Cloud: {e}")
