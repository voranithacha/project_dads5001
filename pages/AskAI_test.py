import streamlit as st
import pandas as pd
import io
from comment_fetcher import get_all_comments
from google import genai

# Function to convert uploaded CSV bytes into a DataFrame
def convert_bytes_to_dataframe(byte_data, encoding='utf-8', **kwargs):
    try:
        string_data = byte_data.decode(encoding)
        data_io = io.StringIO(string_data)
        df = pd.read_csv(data_io, **kwargs)
        return df
    except UnicodeDecodeError as e:
        st.error(f"Decoding error: {e}")
        return None
    except pd.errors.EmptyDataError:
        st.error("Empty data error: The uploaded file is empty.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Load API keys from Streamlit secrets
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


# YouTube video IDs
video_ids = ["OMV9F9zB4KU", "87lJCDADWCo", "CbkX7H-0BIU"]

# Page Header
st.header("🤖 Analysis of BYD YouTube Comment Using Gemini-2.0-Flash")

# Show Videos
# Sidebar for conversation history
with st.sidebar:
    st.subheader("📜 Conversations History")
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    if st.session_state.qa_history:
        for i, item in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
            st.markdown(f"**{i}. คำถาม:** {item['question']}")
            st.markdown(f"✍️ คำตอบ: {item['answer'][:150]}...")
            st.markdown("---")
        if st.button("🗑️ Clear Conversations History"):
            st.session_state.qa_history = []
    else:
        st.info("No Conversations History")

# File Uploader
uf_csv = st.file_uploader("📁 Upload CSV File")
df_dict = None
if uf_csv is not None:
    bytes_data = uf_csv.getvalue()
    df = convert_bytes_to_dataframe(bytes_data, delimiter=',')
    if df is not None:
        st.write(df)
        df_dict = df.to_dict(orient='records')

# Data source selection
option = st.radio("เลือกแหล่งข้อมูลความคิดเห็น", [
    "📁 Access Stored Data (Jun 04, 2025)",
])

# --- Use selected data source ---
if option == "📁 Access Stored Data (Jun 04, 2025)":
    if df_dict:
        st.write(df_dict)

        
client = genai.Client(api_key=GEMINI_API_KEY)

def format_dict_as_text(data_list):
    formatted_rows = ["\n".join([f"{k}: {v}" for k, v in row.items()]) for row in data_list]
    return "\n\n".join(formatted_rows)

def ask_gemini_about_data(client, model, df_dict, question):
    context_text = format_dict_as_text(df_dict)
    prompt = (
        "You are a data analyst. Here's a sample of the data:\n\n"
        f"{context_text}\n\n"
        f"Now answer this question based on the data:\n{question}"
    )
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

st.subheader("🧠 Ask Questions about the Data")

user_question = st.text_input("Enter your question:❓")
if st.button("Ask Gemini") and user_question and df_dict:
    answer = ask_gemini_about_data(client, "gemini-2.0-flash", df_dict, user_question)
    st.write("📌 **Answer:**")
    st.success(answer)
    
    # Save to history
    st.session_state.qa_history.append({
        "question": user_question,
        "answer": answer
    })


    import json

if df_dict:
    st.markdown("### 📤 Export Options")

    # Export as JSON
    json_data = json.dumps(df_dict, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇️ Download JSON",
        data=json_data,
        file_name="comments_data.json",
        mime="application/json"
    )

    # Export as CSV
    csv_data = pd.DataFrame(df_dict).to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="comments_data.csv",
        mime="text/csv"
    )

    # Export as Excel
    excel_buffer = io.BytesIO()
    pd.DataFrame(df_dict).to_excel(excel_buffer, index=False, engine='xlsxwriter')
    st.download_button(
        label="⬇️ Download Excel",
        data=excel_buffer,
        file_name="comments_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

