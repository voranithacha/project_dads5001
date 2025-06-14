import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน")

# กำหนด path ของไฟล์ CSV
csv_path = './data/youtube_comments_full.csv'
st.dataframe(df)


