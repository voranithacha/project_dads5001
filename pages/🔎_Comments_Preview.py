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
                                 "จำนวน Comments ในแต่ละเดือน",
                                 "ตัวอย่าง Comments ในแต่ละหมวด",
                                 "ตัวอย่าง new"
                                
                                 ])
# เงื่อนไขการแสดงผลตามหน้าที่เลือก
if sub_page == "จำนวนการ comments เเต่ละเดือน":
  from pages.Comment_Preview import Count_Comments_Monthly
  Count_Comments_Monthly.run()
elif sub_page == "Word Cloud":
  from pages.Comment_Preview import Word_Cloud
  Word_Cloud.run()
elif sub_page == "ตัวอย่าง new":
  from pages.Comment_Preview import New_test
  New_test.run()
elif sub_page == "Top5 Comments ที่มีจำนวนการ Like เยอะที่สุด":
  st.markdown("### Top5 Comments ที่มีจำนวนการ Like เยอะที่สุด")
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT comment_text_original as comment, like_count FROM yt_comment_full order by like_count desc limit 5;")
  st.write(top_like)
elif sub_page == "Top5 Comments ที่มีจำนวนการ Reply เยอะที่สุด":
  st.markdown("### Top5 Comments ที่มีจำนวนการ Reply เยอะที่สุด")
  con = db.connect('./comment.duckdb')
  top_reply = con.execute("SELECT comment_text_original as comment, reply_count FROM yt_comment_full order by reply_count desc limit 5;")
  st.write(top_reply)
elif sub_page == "Top5 Users ที่มีจำนวนการ Comments เยอะที่สุด":
  st.markdown("### Top5 Users ที่มีจำนวนการ Comments เยอะที่สุด")
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT author_display_name, count(1) as total_comment FROM yt_comment_full group by author_display_name order by count(1) desc limit 5;")
  st.write(top_like)
elif sub_page == "Top5 Comments ที่มีความยาวมากที่สุด":
  st.markdown("### Top5 Comments ที่มีความยาวมากที่สุด")
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT comment_text_original as comment, length(comment_text_original) as length_comment FROM yt_comment_full order by length(comment_text_original) desc limit 5;")
  st.write(top_like)
elif sub_page == "จำนวน Comments ในแต่ละเดือน":
  st.markdown("### จำนวน Comments ในแต่ละเดือน")
  con = db.connect('./comment.duckdb')
  top_like = con.execute("SELECT strftime('%Y-%m', CAST(published_at AS TIMESTAMP)) as year_month , count(1) as total_comment FROM yt_comment_full group by year_month order by year_month asc;")
  st.write(top_like)
elif sub_page == "ตัวอย่าง Comments ในแต่ละหมวด":
  st.markdown("### ตัวอย่าง Comments ในแต่ละหมวด")
  comment_type = st.selectbox("เลือกโมเดลรถ", ["BYD Atto3", "BYD Seal", "BYD Dolphin"])
  car_video_mapping = {"BYD Atto3": "OMV9F9zB4KU", "BYD Seal": "87lJCDADWCo", "BYD Dolphin": "CbkX7H-0BIU"}
  selected_video_id = car_video_mapping[comment_type]
  st.markdown("---")

  st.markdown("### หมวด ราคา 🏷️")
  con = db.connect('comment.duckdb')
  price = con.execute(f"""
  SELECT distinct comment                    
  FROM comment_data 
  WHERE video_id = '{selected_video_id}'
  and (comment like '%ราคา%' or comment like '%ซื้อ%' or comment like '%ขาย%' or comment like '%ถูก%' or comment like '%แพง%')
  limit 5; """).fetchdf()
  st.write(price)
  st.markdown("---")

  st.markdown("### หมวด ประสิทธิภาพ 🛣️")
  efficient = con.execute(f"""
  SELECT distinct comment                    
  FROM comment_data 
  WHERE video_id = '{selected_video_id}'
  and (comment like '%คุณภาพ%' or comment like '%อะไหล่%' or comment like '%พลังงาน%' or comment like '%ถี่%' or comment like '%ทน%')
  limit 5; """).fetchdf()
  st.write(efficient)
  st.markdown("---")

  st.markdown("### หมวด เทคโนโลยี 🧑🏻‍💻")
  tech = con.execute(f"""
  SELECT distinct comment                    
  FROM comment_data 
  WHERE video_id = '{selected_video_id}'
  and (comment like '%ปลอด%' or comment like '%ระบบ%' or comment like '%แจ้งเตือน%' or comment like '%ชาร์จ%' or comment like '%แบต%')
  limit 5; """).fetchdf()
  st.write(tech)
  st.markdown("---")

  st.markdown("### หมวด รูปร่าง 🚘")
  design = con.execute(f"""
  SELECT distinct comment                    
  FROM comment_data 
  WHERE video_id = '{selected_video_id}'
  and (comment like '%สวย%' or comment like '%สี%' or comment like '%ข้างใน%' or comment like '%หน้า%' or comment like '%ดีไซน์%')
  and comment not like '%เสียง%'
  limit 5; """).fetchdf()
  st.write(design)


