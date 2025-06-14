import streamlit as st

# สร้างเมนูด้านข้าง
sub_page = st.sidebar.radio("เลือกหัวข้อการ Preview Comments", ["จำนวนการ comments เเต่ละเดือน",
                                                             "Word Cloud",
                                                             "Top5 Comments ที่มีจำนวน Like เยอะที่สุด", 
                                                             "Top5 Comments ที่มีจำนวน Reply เยอะที่สุด", 
                                                             "Top 5 users ที่มีจำนวน comments เยอะที่สุด",
                                                             "Top5 Comments ที่มีความยาวมากที่สุด",
                                                             ])

# เงื่อนไขการแสดงผลตามหน้าที่เลือก
if sub_page == "จำนวนการ comments เเต่ละเดือน":
    from pages.Comment_Preview import Count_Comments_Monthly
elif sub_page == "Word Cloud":
    from pages.Comment_Preview import Word_Cloud
elif sub_page == "subpage2":
    st.write("คุณเลือกหน้า subpage2")
elif sub_page == "subpage3":
    st.write("คุณเลือกหน้า subpage3")
elif sub_page == "subpage4":
    st.write("คุณเลือกหน้า subpage4")
elif sub_page == "subpage5":
    st.write("คุณเลือกหน้า subpage5")
