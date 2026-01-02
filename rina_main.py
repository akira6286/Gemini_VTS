# rina_main.py
import asyncio
import socket
import pygame
from config import TWITCH_TOKEN, TWITCH_NICK, TWITCH_CHANNEL
from rina_ai_module import get_gemini_response
from rina_VTS_Audio import speak

async def main():
    sock = socket.socket()
    sock.connect(('irc.chat.twitch.tv', 6667))
    sock.send(f"PASS {TWITCH_TOKEN}\r\n".encode('utf-8'))
    sock.send(f"NICK {TWITCH_NICK}\r\n".encode('utf-8'))
    sock.send(f"JOIN {TWITCH_CHANNEL}\r\n".encode('utf-8'))

    pygame.mixer.init()
    print(f"🐾 凜 (模組化版) 已啟動！監控 {TWITCH_CHANNEL}...")

    last_heartbeat = asyncio.get_event_loop().time()

    while True:
        try:
            current_time = asyncio.get_event_loop().time()
            if current_time - last_heartbeat > 60:
                sock.send("PING :tmi.twitch.tv\r\n".encode('utf-8'))
                last_heartbeat = current_time

            sock.settimeout(1.0)
            try:
                data = sock.recv(2048).decode('utf-8')
            except socket.timeout:
                continue

            if "PRIVMSG" in data:
                user = data.split('!', 1)[0][1:]
                message = data.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()
                print(f"📩 {user}: {message}")

                reply_text = get_gemini_response(user, message)
                if reply_text:
                    print(f"🐱 凜：{reply_text}")
                    await speak(reply_text)

        except Exception as e:
            print(f"❌ 錯誤: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
