# project_dads5001


https://projectdads5001-bcvgxba8ftnk7rtutdrreg.streamlit.app/ 

# โครงสร้างโปรเจกต์ (Project Structure)

```plaintext
MainPages.py                     # หน้า Home หรือ Main Dashboard
├── MainApp.py                   # ส่วนรวมของการเรียกใช้งาน (โหลด data, summary ต่าง ๆ)
│
├── pages/                       # โฟลเดอร์รวมทุกหน้าของ Streamlit app
│   ├── Comments_Preview.py           # หน้าดูคอมเมนต์รวม
│   │
│   ├── Commemt_Preview/              # หมวดย่อยของ Comments Preview
│   │   ├── Count_Comments_Monthly.py   # คอมเมนต์รายเดือน
│   │   └── Word_Cloud.py              # หน้าสร้าง Word Cloud
│   │
│   ├── CommentsClassification.py      # หน้าผลการจำแนกความคิดเห็น
│   ├── Ask_Gemini.py                  # AI Insight Assistant
│   │
│   └── Model/                         # โฟลเดอร์โมเดลอยู่ที่นี่
│       ├── final_model_NN.keras
│       └── final_model_rf.pkl
│
├── fonts/                      # ฟอนต์สำหรับภาษาไทย
│   ├── Sarabun-Regular.ttf
│   └── THSarabunNew.ttf
│
├── data/                       # ไฟล์ข้อมูล (CSV/JSON)
│   ├── comments.csv
│   └── data.json
│
├── .streamlit/                 # config สำหรับ Streamlit
│   └── secrets.toml            # API key และ MongoDB URI
│
├── auth/                       # โฟลเดอร์สำหรับระบบล็อกอิน
│   └── user_auth.py
│
├── auth.py                     # ส่วนเสริม auth (session, validate)
├── comment.duckdb              # Local DB
├── comment_fetcher.py          # ตัวดึงคอมเมนต์จาก YouTube / MongoDB
├── requirements.txt            # รายการ dependencies
└── README.md                   # (แนะนำเพิ่มไว้เพื่ออธิบายโปรเจกต์)
```

## คำอธิบายโครงสร้างแต่ละส่วน

- **MainPages.py** — หน้าแรกของเว็บแอป (dashboard หลัก)
- **MainApp.py** — ส่วนกลางสำหรับโหลดข้อมูลและแสดง summary ต่าง ๆ
- **pages/** — รวมไฟล์หน้าต่าง ๆ ของแอป
  - **Comments_Preview.py** — หน้าสำหรับพรีวิวคอมเมนต์
  - **Commemt_Preview/** — หมวดแยกย่อย เช่น สรุปคอมเมนต์รายเดือน, word cloud
  - **CommentsClassification.py** — หน้าแสดงผล AI จำแนกข้อความ
  - **Ask_Gemini.py** — AI Assistant ให้ Insight
  - **Model/** — เก็บไฟล์โมเดล AI ที่เทรนเสร็จแล้ว
- **fonts/** — ฟอนต์ภาษาไทยที่ใช้ใน word cloud หรือกราฟ
- **data/** — ไฟล์ข้อมูล (CSV, JSON ฯลฯ) สำหรับโหลดเข้าแอป
- **.streamlit/** — ไฟล์คอนฟิก Streamlit (เช่น secrets.toml สำหรับ API key ฯลฯ)
- **auth/** — สำหรับระบบล็อกอิน (เช่น user_auth.py)
- **auth.py** — ส่วนเสริมเกี่ยวกับ session และ validation
- **comment.duckdb** — ไฟล์ local database
- **comment_fetcher.py** — โค้ดสำหรับดึงข้อมูลคอมเมนต์จาก YouTube API หรือ MongoDB
- **requirements.txt** — รายการไลบรารีที่ต้องติดตั้ง
- **README.md** — แนะนำและอธิบายโปรเจกต์

> **หมายเหตุ:**  
> - สามารถปรับแก้ไขรายละเอียดใน README.md เพื่อให้ตรงกับโปรเจกต์จริง  
> - เพิ่มรายละเอียดของแต่ละหน้าหรือไฟล์ย่อยได้ตามต้องการ
