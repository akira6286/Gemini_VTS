# rina_main.py
import asyncio
import socket
import pygame
import traceback
import re
from config import TWITCH_TOKEN, TWITCH_NICK, TWITCH_CHANNEL
from rina_ai_module import get_gemini_response
from rina_VTS_Audio import speak, init_vts

# 建立一個訊息佇列
msg_queue = asyncio.Queue()

async def worker():
    print("🐾 [系統] Rinna 的大腦（暱稱識別+打包模式）已啟動...")
    while True:
        try:
            # 1. 先拿第一則訊息
            user, message = await msg_queue.get()

            # 收集這群人的名字 (現在這裡拿到的 user 會是中文暱稱)
            users_in_batch = [user]
            batch_messages = [f"{user}: {message}"]

            # 2. 【核心】人多打包邏輯
            await asyncio.sleep(0.3)

            while not msg_queue.empty() and len(batch_messages) < 5:
                u, m = msg_queue.get_nowait()
                users_in_batch.append(u)
                batch_messages.append(f"{u}: {m}")
                msg_queue.task_done()

            # 3. 合併資訊
            combined_prompt = " | ".join(batch_messages)
            unique_users = ", ".join(list(set(users_in_batch)))

            print(f"📦 [打包處理] 來自 {unique_users} 的 {len(batch_messages)} 則訊息")

            # 4. 呼叫 AI
            loop = asyncio.get_event_loop()
            reply_text = await loop.run_in_executor(None, get_gemini_response, unique_users, combined_prompt)

            if reply_text:
                print(f"🐱 [回覆] 凜奈：{reply_text}")
                await speak(reply_text)
            else:
                print("⚠️ [警告] AI 沒有回傳內容")

            msg_queue.task_done()

        except Exception as e:
            print(f"❌ [Worker 錯誤]:\n{traceback.format_exc()}")

        await asyncio.sleep(0.5)

async def main():
    # 1. 初始化資源
    pygame.mixer.init()

    # 2. 先啟動 Worker
    print("🚀 啟動背景處理任務...")
    asyncio.create_task(worker())

    # 3. 初始化 VTS
    print("📡 正在嘗試連接 VTube Studio...")
    try:
        await asyncio.wait_for(init_vts(), timeout=10.0)
    except Exception as e:
        print(f"⚠️ [VTS 提醒] 連接失敗或超時 ({e})")

    # 4. 連接 Twitch
    print(f"🔌 正在連接到 Twitch 頻道: {TWITCH_CHANNEL}...")
    sock = socket.socket()
    try:
        sock.connect(('irc.chat.twitch.tv', 6667))
        # 【關鍵改動】請求 Twitch 傳送標籤資訊 (包含暱稱)
        sock.send("CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))
        sock.send(f"PASS {TWITCH_TOKEN}\r\n".encode('utf-8'))
        sock.send(f"NICK {TWITCH_NICK}\r\n".encode('utf-8'))
        sock.send(f"JOIN {TWITCH_CHANNEL}\r\n".encode('utf-8'))
    except Exception as e:
        print(f"❌ [Twitch 錯誤] 無法連線: {e}")
        return

    print(f"✅ 系統啟動成功！正在監聽聊天室...")

    last_heartbeat = asyncio.get_event_loop().time()

    while True:
        try:
            current_time = asyncio.get_event_loop().time()
            if current_time - last_heartbeat > 60:
                sock.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
                last_heartbeat = current_time

            sock.settimeout(1.0)
            try:
                raw_data = sock.recv(2048).decode('utf-8')
            except socket.timeout:
                await asyncio.sleep(0.1)
                continue

            # 處理多行數據 (防黏包)
            for line in raw_data.split('\r\n'):
                if not line: continue

                if "PRIVMSG" in line:
                    # --- 解析 Display Name 邏輯 ---
                    display_name = ""
                    # 尋找 display-name=XXX; 標籤
                    match = re.search(r'display-name=([^; ]+)', line)
                    if match:
                        display_name = match.group(1)

                    # 如果找不到標籤中的暱稱，才退回使用原始 ID
                    if not display_name:
                        user_match = re.search(r':([^!]+)!', line)
                        display_name = user_match.group(1) if user_match else "未知觀眾名"

                    # 提取訊息內容
                    msg_parts = line.split('PRIVMSG', 1)
                    if len(msg_parts) > 1:
                        message = msg_parts[1].split(':', 1)[1].strip()
                        print(f"📩 收到來自 {display_name} 的訊息")
                        await msg_queue.put((display_name, message))

        except Exception as e:
            print(f"❌ [迴圈錯誤]: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 程式已由使用者關閉")
