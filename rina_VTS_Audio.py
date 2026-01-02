# vts_audio.py
import asyncio
import re
import pygame
import edge_tts
import io
from pyvts import vts
from config import VTS_CONFIG, MOTION_MAP

async def trigger_vts_motion(motion_name):
    myvts = vts(VTS_CONFIG)
    try:
        await myvts.connect()
        await myvts.request_authenticate_token()
        await myvts.request_authenticate()
        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "ActionRequest",
            "messageType": "HotkeyTriggerRequest",
            "data": { "hotkeyID": motion_name }
        }
        await myvts.request(msg)
        await myvts.close()
    except Exception as e:
        print(f"❌ VTS 失敗: {e}")

async def speak(text):
    if not text: return
    clean_text = re.sub(r'[\*\#\_]', '', text)

    for motion, keywords in MOTION_MAP.items():
        if any(k in clean_text for k in keywords):
            asyncio.create_task(trigger_vts_motion(motion))
            break

    tts = edge_tts.Communicate(clean_text, "zh-TW-HsiaoChenNeural", rate="+15%", pitch="+12Hz")
    audio_data = b""
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    if audio_data:
        pygame.mixer.music.load(io.BytesIO(audio_data), "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
