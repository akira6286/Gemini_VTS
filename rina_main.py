# rina_main.py
import asyncio
import socket
import pygame
import traceback
import re
# 這裡修改：從 config 讀取 TWITCH_CHANNELS 清單
from config import TWITCH_TOKEN, TWITCH_NICK, TWITCH_CHANNELS
from rina_ai_module import get_gemini_response
from rina_VTS_Audio import speak, init_vts, vts_keep_alive_loop

msg_queue = asyncio.Queue()

async def worker():
    """處理訊息打包與 AI 回覆"""
    print("🐾 [系統] Rinna 的大腦已啟動...")
    while True:
        try:
            user, message = await msg_queue.get()
            users_in_batch = [user]
            batch_messages = [f"{user}: {message}"]

            # 短暫等待以打包多則訊息
            await asyncio.sleep(0.3)
            while not msg_queue.empty() and len(batch_messages) < 5:
                u, m = msg_queue.get_nowait()
                users_in_batch.append(u)
                batch_messages.append(f"{u}: {m}")
                msg_queue.task_done()

            combined_prompt = " | ".join(batch_messages)
            unique_users = ", ".join(list(set(users_in_batch)))
            print(f"📦 [打包處理] 來自 {unique_users} 的 {len(batch_messages)} 則訊息")

            loop = asyncio.get_event_loop()
            # 呼叫 Gemini 模組
            reply_text = await loop.run_in_executor(None, get_gemini_response, unique_users, combined_prompt)

            if reply_text:
                print(f"🐱 [回覆] 凜奈：{reply_text}")
                await speak(reply_text)
            msg_queue.task_done()
        except Exception as e:
            print(f"❌ [Worker 錯誤]:\n{traceback.format_exc()}")
        await asyncio.sleep(0.5)

async def twitch_listener(channel_name):
    """專門監聽單一頻道的任務，支援自動重連"""
    print(f"🔌 正在連接到頻道: {channel_name}...")

    while True:
        sock = socket.socket()
        try:
            sock.connect(('irc.chat.twitch.tv', 6667))
            sock.send(f"PASS {TWITCH_TOKEN}\r\n".encode('utf-8'))
            sock.send(f"NICK {TWITCH_NICK}\r\n".encode('utf-8'))
            sock.send(f"JOIN {channel_name}\r\n".encode('utf-8'))
            sock.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))

            print(f"✅ 已進入頻道: {channel_name}")
            last_heartbeat = asyncio.get_event_loop().time()

            while True:
                current_time = asyncio.get_event_loop().time()
                # 每一分鐘發送一次 PING 維持連線
                if current_time - last_heartbeat > 60:
                    sock.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
                    last_heartbeat = current_time

                sock.settimeout(1.0)
                try:
                    raw_data = sock.recv(2048).decode('utf-8')
                except socket.timeout:
                    await asyncio.sleep(0.1)
                    continue

                for line in raw_data.split('\r\n'):
                    if not line: continue
                    if line.startswith("PING"):
                        sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                        continue

                    if "PRIVMSG" in line:
                        display_name = ""
                        match = re.search(r'display-name=([^; ]+)', line)
                        if match: display_name = match.group(1)

                        msg_parts = line.split('PRIVMSG', 1)
                        if len(msg_parts) > 1:
                            message = msg_parts[1].split(':', 1)[1].strip()
                            # 標註來源頻道，讓 AI 知道是誰在熱鬧
                            source_user = f"{display_name}(於 {channel_name})"
                            await msg_queue.put((source_user, message))

        except Exception as e:
            print(f"❌ [頻道 {channel_name} 錯誤]: {e}")

        print(f"🔄 {channel_name} 連線中斷，5 秒後重新嘗試...")
        await asyncio.sleep(5)

async def main():
    pygame.mixer.init()

    # 1. 啟動共通任務
    asyncio.create_task(worker())
    asyncio.create_task(vts_keep_alive_loop()) # 啟動 VTS 監控

    # 2. 為清單中每個頻道啟動獨立監聽器
    for channel in TWITCH_CHANNELS:
        asyncio.create_task(twitch_listener(channel))

    # 讓程式持續運行
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 程式已由使用者關閉")
