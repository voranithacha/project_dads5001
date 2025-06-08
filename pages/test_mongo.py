import streamlit as st
from pymongo import MongoClient
import pandas as pd
#import ast
import sys
import os
import json
#from dotenv import load_dotenv

import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


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
        st.success("เชื่อมต่อกับ MongoDB Atlas สำเร็จ!")
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
st.set_page_config(page_title="MongoDB Comment Explorer", layout="wide")
st.title("💡 MongoDB Comment Explorer with Streamlit")

# ดึง database object
db = get_database()
comments_collection = db.comment

st.write(f"กำลังทำงานกับ Database: **`{db.name}`** และ Collection: **`{comments_collection.name}`**")

# --- ส่วนสำหรับการแสดงข้อมูลทั้งหมด ---
st.header("🔍 ดูข้อมูลคอมเมนต์ทั้งหมด")
if st.button("โหลดคอมเมนต์ทั้งหมด"):
    try:
        all_comments = comments_collection.find({})
        comments_list = list(all_comments) # แปลง Cursor เป็น List เพื่อนำไปแสดงผล
        if comments_list:
            st.json(comments_list) # แสดงผลเป็น JSON format
            st.success(f"พบ {len(comments_list)} คอมเมนต์")
        else:
            st.info("ไม่พบข้อมูลใน Collection นี้")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

# --- ส่วนสำหรับการค้นหาข้อมูล (Filter) ---
st.header("🔎 ค้นหาคอมเมนต์")

# input สำหรับ video_id
search_video_id = st.text_input("ค้นหาด้วย Video ID (เช่น OMV9F9zB4KU):")

# input สำหรับ author
search_author = st.text_input("ค้นหาด้วย Author (เช่น @millenear-km2ue):")

# input สำหรับคำค้นใน comment หรือ video_title
search_keyword = st.text_input("ค้นหาคำใน Comment หรือ Video Title:")

# ปุ่มค้นหา
if st.button("ค้นหาข้อมูล"):
    query = {}
    if search_video_id:
        query["video_id"] = search_video_id
    if search_author:
        query["author"] = search_author
    if search_keyword:
        # ใช้ $or เพื่อค้นหาใน comment หรือ video_title
        query["$or"] = [
            {"comment": {"$regex": search_keyword, "$options": "i"}},
            {"video_title": {"$regex": search_keyword, "$options": "i"}}
        ]

    st.write(f"กำลังใช้ Query: `{query}`")

    try:
        # ใช้ .limit() และ .sort() เพื่อจำกัดผลลัพธ์และเรียงลำดับ (ถ้าต้องการ)
        results = comments_collection.find(query).limit(100).sort("video_id", 1) # จำกัด 100 ผลลัพธ์, เรียงตาม video_id
        results_list = list(results)

        if results_list:
            st.json(results_list)
            st.success(f"พบ {len(results_list)} ผลลัพธ์")
        else:
            st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการค้นหา: {e}")

# --- ส่วนสำหรับนับจำนวนเอกสาร ---
st.header("📊 สถิติ")
try:
    total_comments = comments_collection.count_documents({})
    st.info(f"จำนวนคอมเมนต์ทั้งหมดใน Collection: **{total_comments}**")
except Exception as e:
    st.error(f"ไม่สามารถนับจำนวนเอกสารได้: {e}")