import streamlit as st

st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling", "📈 Result Visualization"])

# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    # ดึงคอมเมนต์จาก MongoDB หรือ CSV แล้วโชว์
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")
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
data = pd.DataFrame(data)         # Convert to DataFrame
 
# Query only video_title
comments = list(collection.find({}, {"video_title": 1}))
df = pd.DataFrame(comments)
 
# Check column
if 'video_title' not in df.columns:
    st.error("ไม่พบคอลัมน์ 'video_title'")
else:
    # Count frequency of each title
    video_counts = df['video_title'].value_counts().reset_index()
    video_counts.columns = ['video_title', 'count']
 
    # Create dynamic label based on keywords
    def generate_label(title):
        title_upper = title.upper()  # ป้องกันตัวเล็กใหญ่
        if "ATTO" in title_upper:
            return "BYD Atto3"
        elif "SEAL" in title_upper:
            return "BYD Seal"
        elif "DOLPHIN" in title_upper:
            return "BYD Dolphin"
        else:
            return "อื่น ๆ"  # หรือจะ return title เองก็ได้
 
    # Apply label
    video_counts["label"] = video_counts["video_title"].apply(generate_label)
 
    # Reorder columns
    result_df = video_counts[["label", "video_title", "count"]]
 
    # Display
    st.subheader("📊 Video Comment Counts")
    st.dataframe(result_df)
 










# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.subheader("🧪 สร้างโมเดล Machine Learning")
    # เลือก model (Naive Bayes, SVM, etc.)
    model_type = st.selectbox("เลือกโมเดล", ["Naive Bayes", "SVM", "Random Forest"])
    st.write(f"คุณเลือกโมเดล: {model_type}")

# --- Section 3 ---
elif option == "📈 Result Visualization":
    st.subheader("📈 ผลการจำแนกคอมเมนต์")
    # แสดง confusion matrix หรือ accuracy score
    st.write("แสดงกราฟ performance ของโมเดล")

