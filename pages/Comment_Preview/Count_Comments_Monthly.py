import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from sklearn.feature_extraction.text import CountVectorizer
import re
import os

def run():
    # === PATH CONFIG ===
    CSV_PATH = './data/youtube_comments_full.csv'
    FONT_PATH = './fonts/Sarabun-Regular.ttf'
    
    st.subheader("☁️ Word Cloud จากความคิดเห็นใน YouTube")
    
    # === FILE CHECK ===
    if not os.path.exists(CSV_PATH):
        st.error(f"ไม่พบไฟล์ที่ {CSV_PATH}")
    else:
        df = pd.read_csv(CSV_PATH)
        if "comment_text_display" not in df.columns:
            st.error("ไม่พบคอลัมน์ 'comment_text_display' ในไฟล์ CSV นี้")
        else:
            st.write(df)
            




