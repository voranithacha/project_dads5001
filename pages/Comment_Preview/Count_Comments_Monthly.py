import pandas as pd
import streamlit as st
import os

def run():
  # === PATH CONFIG ===
  CSV_PATH = './data/youtube_comments_full.csv'
  
  st.subheader("📊 จำนวนการแสดงความคิดเห็นในแต่ละเดือน (CSV)")


