import streamlit as st


# สร้างเมนูด้านข้าง
sub_page = st.sidebar.radio("เลือกหน้า Word Cloud", ["Word Cloud", "subpage2", "subpage3", "subpage4", "subpage5"])

# เงื่อนไขการแสดงผลตามหน้าที่เลือก
if sub_page == "Word Cloud":
    from pages.Comment_Preview import Word_Cloud
    Word_Cloud.show()

elif sub_page == "subpage2":
    st.write("คุณเลือกหน้า subpage2")
elif sub_page == "subpage3":
    st.write("คุณเลือกหน้า subpage3")
elif sub_page == "subpage4":
    st.write("คุณเลือกหน้า subpage4")
elif sub_page == "subpage5":
    st.write("คุณเลือกหน้า subpage5")
