import streamlit as st
from collections import Counter
import pandas as pd
from pymongo import MongoClient
import json

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
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # adjust if needed
db = client["db_comment"]
collection = db["comments"]
# Load JSON data
with open("D:\DADS5001 - Tools\data\comments_data.json", "r", encoding="utf-8") as f:
    try:
        data = json.load(f)  # for array format
    except json.JSONDecodeError:
        # fallback if JSON is in NDJSON format
        data = [json.loads(line) for line in f]

collection.delete_many({})  #ลบก่อน insert

# Insert into MongoDB
if isinstance(data, list):
    collection.insert_many(data)
else:
    collection.insert_one(data)

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