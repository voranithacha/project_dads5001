import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from sklearn.feature_extraction.text import CountVectorizer
import re
import os

# === PATH CONFIG ===
CSV_PATH = r"D:\Master Degree\Tools\Project\youtube_comments2.csv"
FONT_PATH = r"D:\Master Degree\Tools\Project\Sarabun\Sarabun-Regular.ttf"

st.title("☁️ Word Cloud จากความคิดเห็น YouTube (วลี, คำ, คำนาม, คำกริยา)")

# === FILE CHECK ===
if not os.path.exists(CSV_PATH):
    st.error(f"ไม่พบไฟล์ที่ {CSV_PATH}")
else:
    df = pd.read_csv(CSV_PATH)
    
    if "comment_text_display" not in df.columns:
        st.error("ไม่พบคอลัมน์ 'comment_text_display' ในไฟล์ CSV นี้")
    else:
        # === เตรียมข้อความ ===
        raw_text = " ".join(df["comment_text_display"].dropna().astype(str))
        cleaned_text = re.sub(r"[^\u0E00-\u0E7Fa-zA-Z\s]", "", raw_text)

        # === ตัดคำ และ POS tagging ===
        tokens = word_tokenize(cleaned_text, engine="newmm")
        tokens = [w.lower() for w in tokens if len(w) > 1 and w.isalpha()]
        tagged = pos_tag(tokens, engine="perceptron")

        nouns = [word for word, pos in tagged if pos.startswith("N")]
        verbs = [word for word, pos in tagged if pos.startswith("V")]

        # === วลี 2-3 คำ ===
        processed_text = " ".join(tokens)
        vectorizer = CountVectorizer(ngram_range=(2,3))
        X = vectorizer.fit_transform([processed_text])
        phrases_freq = dict(zip(vectorizer.get_feature_names_out(), X.toarray().sum(axis=0)))

        # === ความถี่คำ ===
        word_freq_all = {}
        for w in tokens:
            word_freq_all[w] = word_freq_all.get(w, 0) + 1
        
        word_freq_nouns = {}
        for w in nouns:
            word_freq_nouns[w] = word_freq_nouns.get(w, 0) + 1
        
        word_freq_verbs = {}
        for w in verbs:
            word_freq_verbs[w] = word_freq_verbs.get(w, 0) + 1

        def show_wordcloud(freq_dict, title, width=800, height=400, font_size="16px"):
            if not freq_dict:
                st.warning(f"ไม่พบข้อมูลสำหรับ {title}")
                return
            wordcloud = WordCloud(
                font_path=FONT_PATH,
                width=width,
                height=height,
                background_color="white",
                colormap="Set2"
            ).generate_from_frequencies(freq_dict)
             # ใช้ HTML ย่อขนาดหัวข้อ
            st.markdown(f"<p style='font-size:{font_size}; font-weight:bold'>{title}</p>", unsafe_allow_html=True)

            fig, ax = plt.subplots(figsize=(width/100, height/100))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        # === Layout: ซ้าย (วลี) | ขวา (คำ) ===
        col1, col2 = st.columns([1.5, 1])

        with col1:
            show_wordcloud(phrases_freq, "🔤 วลี 2-3 คำ", width=400, height=485)

        with col2:
            #show_wordcloud(word_freq_all, "🔡 คำทั้งหมด", width=400, height=200)
            show_wordcloud(word_freq_nouns, "📘 คำนาม", width=400, height=300)
            show_wordcloud(word_freq_verbs, "📗 คำกริยา", width=400, height=300)
