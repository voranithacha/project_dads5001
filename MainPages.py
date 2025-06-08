import streamlit as st
import pandas as pd
import duckdb as db
import os

st.write("## Starbucks Dataset :coffee::mermaid:")

file_path = './data/Starbucks.csv'
df = pd.read_csv(file_path)
#df = pd.read_csv("Starbucks.csv")

st.write(df)


results1 = db.sql(f"""
    SELECT count(*) as count
    FROM df 
""").df()

results2 = db.sql(f"""
    SELECT count(*) as count from (select distinct Country from df)a
""").df()

results3 = db.sql(f"""
    SELECT count(*) as count from (select distinct "Ownership Type" from df)a
""").df()


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 23px;'>Total shop 🏡</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 20px;'>{str(results1.iloc[0, 0])}</h1></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 23px;'>Total Country 🗺️</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 20px;'>{str(results2.iloc[0, 0])}</h1></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 23px;'>Ownership Type 🧑‍🤝‍🧑</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 20px;'>{str(results3.iloc[0, 0])}</h1></div>", unsafe_allow_html=True)

st.markdown(f"<div margin-top: 20%;'><h2 style='font-size: 22px;'></h2></div>", unsafe_allow_html=True)
st.markdown(f"<div margin-top: 20%;'><h2 style='font-size: 22px;'>Member</h2></div>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 18px;'>1. Sirima Pangpradang  6710422001</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 18px;'>2. Seriphap Siangnok   6710422002</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 18px;'>3. Voranitha Chaiaroon 6710422013</p>", unsafe_allow_html=True)