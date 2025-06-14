import streamlit as st
import duckdb as db


st.title("🧠 Comment Classification")

# --- Sub-topic Navigation ---
option = st.radio("เลือกหัวข้อย่อย", ["🔍 Preview Comments", "🧪 ML Modeling"])

# --- Section 1 ---
if option == "🔍 Preview Comments":
    st.subheader("🔍 ดูตัวอย่างคอมเมนต์")
    st.write("แสดงคอมเมนต์ top 5 ที่เกี่ยวกับแต่ละหมวด")

    con = db.connect('./comment.duckdb')
    con.execute("CREATE OR REPLACE TABLE yt_comment_full AS SELECT * FROM read_csv_auto('./data/youtube_comments_full.csv')")

    # comment Top5 (liked)
    st.write("Top 5 comments with Most Liked")
    top_like = con.execute("SELECT comment_text_original as comment, like_count FROM yt_comment_full order by like_count desc limit 5;")
    st.write(top_like)
    # comment Top5 (replied)
    st.write("Top 5 comments with Most Replied Comments")
    top_reply = con.execute("SELECT comment_text_original as comment, reply_count FROM yt_comment_full order by reply_count desc limit 5;")
    st.write(top_reply)
    # Top 5 user ที่ comment เยอะสุด(comment หลาย comment) 
    st.write("Top 5 Users with the Most Comments")
    top_like = con.execute("SELECT author_display_name, count(1) as total_comment FROM yt_comment_full group by author_display_name order by count(1) desc limit 5;")
    st.write(top_like)
    # Top 5 comment ที่ยาวที่สุด
    st.write("Top 5 long Comments")
    top_like = con.execute("SELECT comment_text_original as comment, length(comment_text_original) as length_comment FROM yt_comment_full order by length(comment_text_original) desc limit 5;")
    st.write(top_like)
    # count comment เเบ่งเป็นเดือน
    st.write("Total comment of each year")
    top_like = con.execute("SELECT strftime('%Y-%m', CAST(published_at AS TIMESTAMP)) as year_month , count(1) as total_comment FROM yt_comment_full group by year_month order by year_month asc;")
    st.write(top_like)

    st.markdown("---")

    comment_type = st.selectbox("เลือกโมเดลรถ", ["BYD Atto3", "BYD Seal", "BYD Dolphin"])
    car_video_mapping = {"BYD Atto3": "OMV9F9zB4KU", "BYD Seal": "87lJCDADWCo", "BYD Dolphin": "CbkX7H-0BIU"}
    selected_video_id = car_video_mapping[comment_type]
    st.markdown("---")

    st.write("หมวด ราคา")
    con = db.connect('./comment.duckdb')
    price = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%ราคา%' or comment like '%ซื้อ%' or comment like '%ขาย%' or comment like '%ถูก%' or comment like '%แพง%')
    limit 5; """).fetchdf()
    st.write(price)
    st.markdown("---")

    st.write("หมวด ประสิทธิภาพ")
    efficient = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%คุณภาพ%' or comment like '%อะไหล่%' or comment like '%พลังงาน%' or comment like '%ถี่%' or comment like '%ทน%')
    limit 5; """).fetchdf()
    st.write(efficient)
    st.markdown("---")

    st.write("หมวด เทคโนโลยี")
    tech = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%ปลอด%' or comment like '%ระบบ%' or comment like '%แจ้งเตือน%' or comment like '%ชาร์จ%' or comment like '%แบต%')
    limit 5; """).fetchdf()
    st.write(tech)
    st.markdown("---")

    st.write("หมวด รูปร่าง")
    design = con.execute(f"""
    SELECT distinct comment                    
    FROM comment_data 
    WHERE video_id = '{selected_video_id}'
    and (comment like '%สวย%' or comment like '%สี%' or comment like '%ข้างใน%' or comment like '%หน้า%' or comment like '%ดีไซน์%')
    limit 5; """).fetchdf()
    st.write(design)


# --- Section 2 ---
elif option == "🧪 ML Modeling":
    st.markdown("[ไปที่ ML Modeling](https://projectdads5001-otbopsjs5ndt36ag2gtdm3.streamlit.app/ML_trial1)")


