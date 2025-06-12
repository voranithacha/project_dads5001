import streamlit as st
from collections import Counter
import pandas as pd
from pymongo import MongoClient
import json

#for word clound
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.corpus import common
from pythainlp.util import Trie
import re

st.title("YouTube Comments Analysis")
st.markdown("""
### 🔰 Introduction
Applying machine learning techniques to text classification. Its primary objective is to automatically categorize comments from YouTube car review videos into predefined categories, enabling deeper insights into public sentiment and user feedback.
"""
"""### 🔍 Data Source and Collection
Text Comments: Extracted from the comment sections of YouTube car review videos.  
Target Brand: BYD, with a focus on its three best-selling models in the Thai market — Atto 3, Seal, and Dolphin.  
YouTube Channel: Data was collected from the official *autolifethailand* channel, a trusted automotive source with over 1.06 million subscribers. 
Comments were gathered from three BYD-related review videos, which form the basis for training and evaluating the classification model.
"""
"""### 💡 AI-Powered Insight Assistant
To enhance the value of this project, an AI-powered assistant feature is included for premium users. This tool enables interactive exploration of classified comments, identifies key discussion points, highlights emerging trends, and provides contextual insight summaries—supporting smarter and faster decision-making driven by public opinion.
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

# --- สร้าง Custom Dictionary ---
# โหลดพจนานุกรมมาตรฐานของ pythainlp
default_words = common.thai_words()
custom_word_list = list(default_words) + ["ไฟฟ้า", "รถยนต์ไฟฟ้า", "แบตเตอรี่", "ขับขี่","ซื้อ","เงิน","เสียง","อะไหล่","แจ้งเตือน","ชาร์จ","กล้อง","เทค","ออฟชั่น","สี","ข้างใน","หน้า","ดีไซน์"] 
custom_dictionary = Trie(custom_word_list)
# ----------------------------------

# --- สร้าง Word Cloud ---
# --- กำหนด Mapping ชื่อ Model กับ Keyword ใน title ---
model_keywords = {
    "BYD Atto3": "ATTO",
    "BYD Dolphin": "DOLPHIN",
    "BYD Seal": "SEAL"
}
st.header("☁️ Word Cloud")
# --- สร้าง Dropdown ให้ผู้ใช้เลือก Model ---
selected_model = st.selectbox("เลือกรุ่นรถยนต์ที่ต้องการดู Word Cloud", list(model_keywords.keys()))

if selected_model: # ตรวจสอบแค่ว่ามีการเลือกโมเดลแล้วหรือไม่
    try:
        keyword = model_keywords[selected_model]

        # --- ส่วนนี้คือการ Query จาก MongoDB จริงของคุณ ---
        cursor = comments_collection.find(
            {"video_title": {"$regex": keyword, "$options": "i"}},
            {"comment": 1}
        )
        # ---------------------------------------------------

        # ดึงและทำความสะอาดข้อความ
        comments = [re.sub(r"[^\u0E00-\u0E7F\s]+", " ", doc.get("comment", "")) for doc in cursor]
        full_text = " ".join(comments)

        # ตรวจสอบว่ามีข้อความให้ประมวลผลหรือไม่
        if not full_text.strip():
            st.warning(f"ไม่พบข้อมูลคอมเมนต์สำหรับรุ่น **{selected_model}** ที่มีคีย์เวิร์ด **'{keyword}'**")
            # ไม่ต้อง st.stop() ถ้าอยากให้ dropdown ยังใช้งานได้ต่อเนื่อง
        else: # เพิ่ม else block เพื่อให้ Word Cloud สร้างเมื่อมีข้อมูลเท่านั้น
            # ตัดคำโดยใช้ Custom Dictionary
            tokens = word_tokenize(full_text, engine="newmm", custom_dict=custom_dictionary)

            # กำหนด Stopwords ที่ครอบคลุมมากขึ้น
            combined_stopwords = set(thai_stopwords()).union({
                "ครับ","ค่ะ","ๆ","นะ","เลย","เป็น","คือ","ว่า","ได้","จะ","ก็","แล้ว","มาก","น้อย","ไป","มา","อยู่","มี","ไม่","คน","คัน","ตัว","รุ่น","ทำไม","แบบนี้","เห็น","เหมือน","ใน","รูป","ถูก"
            })

            # กำหนด Allowed Words (คำที่คุณต้องการให้แสดงเท่านั้น)
            allowed_words = {
                "ดี", "แรง", "ประหยัด", "สวย", "น่ารัก", "ราคา", "คุ้ม", "สบาย", "เร็ว", "เงียบ",
                "ซื้อ", "ขาย", "ถูก", "แพง", "ลด", "บาท", "ล้าน", "แสน", "เงิน", "เสียง",
                "ขับขี่","พลังงาน","ถี่","ทน","คุณภาพ","อะไหล่","ปลอด","ระบบ",
                "แจ้งเตือน", "ชาร์จ", "กล้อง", "แบต", "ช่วย", "เทค", "ออฟชั่น", "ไฟฟ้า",
                "สี", "ภาย", "ข้างใน", "ทรง", "รูป", "หน้า", "หรู", "หรา", "นอก", "งาม", "ดีไซน์",
                "รถยนต์ไฟฟ้า", "แบตเตอรี่", "รูปลักษณ์", "สมรรถนะ", "ความปลอดภัย"
            }
            
            # กรองคำ
            filtered_tokens = [w for w in tokens if w not in combined_stopwords and len(w) > 1 and w in allowed_words]

            # หากไม่มีคำที่ถูกกรองเลย ให้แจ้งเตือน
            if not filtered_tokens:
                st.warning(f"ไม่พบคำสำคัญที่เลือกในคอมเมนต์สำหรับรุ่น **{selected_model}**")
            else: # สร้าง Word Cloud เมื่อมี filtered_tokens เท่านั้น
                # สร้าง Word Cloud
                wordcloud = WordCloud(
                    font_path="fonts/THSarabunNew.ttf",
                    width=800,
                    height=400,
                    background_color="white",
                    collocations=False
                ).generate(" ".join(filtered_tokens))

                # แสดงผล
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
                st.success(f"แสดง Word Cloud สำหรับ: **{selected_model}**")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้าง Word Cloud: {e}")
