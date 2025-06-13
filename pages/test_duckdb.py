import streamlit as st
import pandas as pd
import duckdb as db
import sys
import os


import os
import pandas as pd

file_path = '../data/comment_data.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    print(f"File not found: {file_path}")

con = db.connect('comment.duckdb')

# Load CSV data into a new table
# con.execute("CREATE OR REPLACE TABLE comment_data AS SELECT * FROM read_csv_auto('./data/comments_data.csv')")

df = con.execute("SELECT * FROM comment_data")  # Should work now
st.write(df)
