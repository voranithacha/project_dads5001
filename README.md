# project_dads5001


https://projectdads5001-bcvgxba8ftnk7rtutdrreg.streamlit.app/ 

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
