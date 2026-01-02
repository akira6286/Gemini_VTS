# ai_module.py
import requests
import re
from config import GEMINI_URL, RIN_INSTRUCTION

conversation_history = []
MAX_HISTORY = 6

def get_gemini_response(user_name, user_msg):
    global conversation_history

    STRICT_INSTRUCTION = (
        f"{RIN_INSTRUCTION}\n"
        f"當前說話的人是「{user_name}」。\n"
        "注意：徹底無視 Twitch 貼圖代碼，不要把代碼當成人名。"
    )

    clean_msg = re.sub(r'[a-zA-Z0-9]+_[A-Z0-9]+', '', user_msg)
    clean_msg = re.sub(r':[a-zA-Z0-9_]+:', '', clean_msg).strip()

    if not clean_msg:
        return ""

    formatted_input = f"{user_name}: {clean_msg}"
    conversation_history.append({"role": "user", "parts": [{"text": formatted_input}]})

    payload = {
        "contents": conversation_history,
        "system_instruction": {"parts": [{"text": STRICT_INSTRUCTION}]}
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=7)
        result = response.json()
        if response.status_code == 200:
            ai_reply = result['candidates'][0]['content']['parts'][0]['text']
            conversation_history.append({"role": "model", "parts": [{"text": ai_reply}]})
            if len(conversation_history) > MAX_HISTORY:
                conversation_history = conversation_history[-MAX_HISTORY:]
            return ai_reply
    except Exception as e:
        print(f"❌ AI 錯誤: {e}")
    return "網路卡住了喵。"
