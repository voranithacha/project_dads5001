import streamlit as st
import duckdb as db

# เพิ่มหัวข้อขนาดใหญ่ใน sidebar ก่อน radio
st.sidebar.markdown("<h3 style='font-size:20px;'>📌 เลือกหัวข้อการ Preview Comments</h3>", unsafe_allow_html=True)
# สร้างเมนูด้านข้าง
sub_page = st.sidebar.radio("", ["จำนวนการ comments เเต่ละเดือน",
                                 "Word Cloud",
                                 "Top5 Comments ที่มีจำนวนการ Like เยอะที่สุด", 
                                 "Top5 Comments ที่มีจำนวนการ Reply เยอะที่สุด", 
                                 "Top5 Users ที่มีจำนวนการ Comments เยอะที่สุด",
                                 "Top5 Comments ที่มีความยาวมากที่สุด",
                                 "จำนวน Comments ในแต่ละเดือน"
                                 ])
# เงื่อนไขการแสดงผลตามหน้าที่เลือก
if sub_page == "จำนวนการ comments เเต่ละเดือน":
  from pages.Comment_Preview import Count_Comments_Monthly
  Count_Comments_Monthly.run()
elif sub_page == "Word Cloud":
  from pages.Comment_Preview import Word_Cloud
  Word_Cloud.run()
elif sub_page == "Top5 Comments ที่มีจำนวนการ Like เยอะที่สุด":
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT comment_text_original as comment, like_count FROM yt_comment_full order by like_count desc limit 5;")
  st.write(top_like)
elif sub_page == "Top5 Comments ที่มีจำนวนการ Reply เยอะที่สุด":
  con = db.connect('./comment.duckdb')
  top_reply = con.execute("SELECT comment_text_original as comment, reply_count FROM yt_comment_full order by reply_count desc limit 5;")
  st.write(top_reply)
elif sub_page == "Top5 Users ที่มีจำนวนการ Comments เยอะที่สุด":
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT author_display_name, count(1) as total_comment FROM yt_comment_full group by author_display_name order by count(1) desc limit 5;")
  st.write(top_like)
elif sub_page == "Top5 Comments ที่มีความยาวมากที่สุด":
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT comment_text_original as comment, length(comment_text_original) as length_comment FROM yt_comment_full order by length(comment_text_original) desc limit 5;")
  st.write(top_like)
elif sub_page == "จำนวน Comments ในแต่ละเดือน":
  top_like = con.execute("SELECT strftime('%Y-%m', CAST(published_at AS TIMESTAMP)) as year_month , count(1) as total_comment FROM yt_comment_full group by year_month order by year_month asc;")
  st.write(top_like)
