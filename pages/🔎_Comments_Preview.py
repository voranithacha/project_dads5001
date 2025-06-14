import streamlit as st

# เพิ่มหัวข้อขนาดใหญ่ใน sidebar ก่อน radio
st.sidebar.markdown("<h3 style='font-size:20px;'>📌 เลือกหัวข้อการ Preview Comments</h3>", unsafe_allow_html=True)
# สร้างเมนูด้านข้าง
sub_page = st.sidebar.radio("", ["จำนวนการ comments เเต่ละเดือน",
                                 "Word Cloud",
                                 "Top5 Comments ที่มีจำนวนการ Like เยอะที่สุด", 
                                 "Top5 Comments ที่มีจำนวนการ Reply เยอะที่สุด", 
                                 "Top5 Users ที่มีจำนวนการ Comments เยอะที่สุด",
                                 "Top5 Comments ที่มีความยาวมากที่สุด",
                                 ])
# เงื่อนไขการแสดงผลตามหน้าที่เลือก
if sub_page == "จำนวนการ comments เเต่ละเดือน":
  from pages.Comment_Preview import Count_Comments_Monthly
  Count_Comments_Monthly.run()
elif sub_page == "Word Cloud":
  from pages.Comment_Preview import Word_Cloud
  Word_Cloud.run()
elif sub_page == "subpage3":
  st.write("คุณเลือกหน้า subpage3")
elif sub_page == "subpage4":
  st.write("คุณเลือกหน้า subpage4")
elif sub_page == "subpage5":
  st.write("คุณเลือกหน้า subpage5")
elif sub_page == "subpage6":
  st.write("คุณเลือกหน้า subpage6")
