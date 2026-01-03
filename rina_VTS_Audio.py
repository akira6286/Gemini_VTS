# vts_audio.py
import asyncio
import re
import pygame
import edge_tts
import io
from pyvts import vts
from config import VTS_CONFIG, MOTION_MAP

# 建立一個全域的 VTS 實例，避免重複登入
myvts = vts(VTS_CONFIG)

async def init_vts():
    """在程式啟動時呼叫一次，建立長連接"""
    try:
        await myvts.connect()
        await myvts.request_authenticate_token()
        await myvts.request_authenticate()
        print("✅ [VTS] 長連接已建立")
    except Exception as e:
        print(f"❌ [VTS] 初始化失敗: {e}")

async def trigger_vts_motion(motion_name):
    """因為已經連線了，現在觸發動作幾乎是瞬間的"""
    try:
        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "ActionRequest",
            "messageType": "HotkeyTriggerRequest",
            "data": { "hotkeyID": motion_name }
        }
        await myvts.request(msg)
    except Exception as e:
        print(f"❌ [VTS] 動作發送失敗: {e}")

async def speak(text):
    if not text: return
    # 過濾雜質，減少 TTS 引擎負擔
    clean_text = re.sub(r'[\*\#\_]', '', text)

    # 1. 提前觸發 VTS 動作 (不再等待，直接用背景任務丟出去)
    for motion, keywords in MOTION_MAP.items():
        if any(k in clean_text for k in keywords):
            asyncio.create_task(trigger_vts_motion(motion))
            break

    # 2. 極速語音設定：語速 +30% 可以顯著縮短播放時間
    tts = edge_tts.Communicate(clean_text, "zh-TW-HsiaoChenNeural", rate="+30%", pitch="+10Hz")

    audio_data = b""
    # 這裡我們還是先抓取完整數據，但優化內存播放
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    if audio_data:
        # 使用 BytesIO 讓 Pygame 直接從記憶體讀取，跳過硬碟 IO
        f = io.BytesIO(audio_data)
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()

        # 縮短輪詢間隔，讓下一句能更快接上
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)

        pygame.mixer.music.unload()
