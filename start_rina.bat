@echo off
:: 在第一行放一個沒意義的跳轉，保護後面的指令不被編碼標記毀掉
goto START

:START
cd /d "%~dp0"
chcp 65001 > nul

echo === Environment Check ===
:: 檢查 python 指令是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 找不到 python 指令，請重新安裝並勾選 Add to PATH。
    pause
    exit
)

:: 檢查核心檔案是否存在
if not exist rina_main.py (
    echo [ERROR] 找不到 rina_main.py，請確認檔案位置！
    pause
    exit
)

:: 安裝套件
python -m pip install pygame-ce requests edge-tts pyvts

:: 檢查設定檔
if exist config.py goto RUN_APP

echo === Setup Config ===
set /p API_KEY="GEMINI_API_KEY: "
set /p T_TOKEN="TWITCH_TOKEN: "
set /p T_NICK="TWITCH_NICK: "
set /p T_CHANNEL="TWITCH_CHANNEL: "

(
echo GEMINI_API_KEY = "%API_KEY%"
echo TWITCH_TOKEN = "%T_TOKEN%"
echo TWITCH_NICK = "%T_NICK%"
echo TWITCH_CHANNEL = "%T_CHANNEL%"
echo MODEL_ID = "gemini-2.5-flash"
echo GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GEMINI_API_KEY}"
echo VTS_CONFIG = { "host": "127.0.0.1", "port": 8001, "plugin_name": "Rina_VTS_gemini", "developer": "Akira", "authentication_token_path": "./new_token.json" }
echo MOTION_MAP = { "wave_motion": ["哈囉"], "EXP_Heart": ["愛妳"] }
echo RIN_INSTRUCTION = """妳是「凜奈」。"""
) > config.py

:RUN_APP
echo === Starting Rinna ===
:: 執行主程式
python rina_main.py
if errorlevel 1 pause