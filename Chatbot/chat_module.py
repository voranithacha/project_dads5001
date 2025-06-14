def ask_bot(message):
   
    if "สวัสดี" in message:
        return "สวัสดีครับ ยินดีช่วยเหลือ!"
    elif "ชื่ออะไร" in message:
        return "ฉันคือ AskAI จาก DADS5001"
    else:
        return "ขออภัย ฉันยังไม่เข้าใจคำถามนี้"
