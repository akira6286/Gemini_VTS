# rina_VTS_Audio.py
import asyncio
import re
import pygame
import edge_tts
import io
from pyvts import vts
from config import VTS_CONFIG, MOTION_MAP

# 建立一個全域的 VTS 實例
myvts = vts(VTS_CONFIG)
vts_connected = False
vts_lock = asyncio.Lock() # 關鍵：增加鎖定機制，防止同時收發

async def init_vts():
    """建立連線並驗證"""
    global vts_connected
    async with vts_lock: # 使用鎖確保初始化時不會被干擾
        try:
            await myvts.connect()
            await myvts.request_authenticate_token()
            await myvts.request_authenticate()
            vts_connected = True
            print("✅ [VTS] 連線與授權成功")
        except Exception as e:
            vts_connected = False
            print(f"❌ [VTS] 初始化失敗: {e}")

async def safe_request(payload):
    """安全發送請求的統一入口，解決 recv 衝突問題"""
    global vts_connected
    if not vts_connected: return

    async with vts_lock: # 確保同一時間只有一個協程在操作 VTS 通訊
        try:
            return await myvts.request(payload)
        except Exception as e:
            if "recv" in str(e).lower():
                pass # 忽略重複 recv 的警告
            else:
                print(f"❌ [VTS] 請求失敗: {e}")
                vts_connected = False

async def vts_keep_alive_loop():
    """心跳偵測：使用統一的安全發送入口"""
    global vts_connected
    while True:
        if vts_connected:
            ping_msg = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "Heartbeat",
                "messageType": "APIStateRequest"
            }
            await safe_request(ping_msg)
        else:
            print("🔄 [VTS] 偵測到未連線，開始重連...")
            await init_vts()
        await asyncio.sleep(15)

async def trigger_vts_motion(motion_name):
    """觸發動作：使用統一的安全發送入口"""
    msg = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "MotionRequest",
        "messageType": "HotkeyTriggerRequest",
        "data": { "hotkeyID": motion_name }
    }
    await safe_request(msg)

async def speak(text):
    """語音播放與連動動作"""
    if not text: return
    clean_text = re.sub(r'[\*\#\_]', '', text)

    # 1. 動作觸發
    if vts_connected:
        for motion, keywords in MOTION_MAP.items():
            if any(k in clean_text for k in keywords):
                # 直接 await 確保動作指令送出後才進行下一步
                asyncio.create_task(trigger_vts_motion(motion))
                break

    # 2. TTS 語音生成與播放 (維持原樣)
    tts = edge_tts.Communicate(clean_text, "zh-TW-HsiaoChenNeural", rate="+30%", pitch="+10Hz")
    audio_data = b""
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    if audio_data:
        f = io.BytesIO(audio_data)
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        pygame.mixer.music.unload()
