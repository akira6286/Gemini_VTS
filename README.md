# 🐾 Rinna Twitch Bot (凜奈) - 異步架構 VTS 連動 AI 機器人

這是一個專為 VTuber 設計，結合了 **Gemini AI**、**Edge-TTS** 語音合成，以及 **VTube Studio** 動作連動的 Twitch 聊天室機器人。

## 🌟 功能亮點
- **非同步任務隊列**：基於 `asyncio` 的異步架構，確保監聽聊天室、AI 生成與語音播放並行不卡頓。
- **智能訊息打包 (Message Batching)**：人多時自動打包多則訊息統一回覆，讓對話更具直播互動感。
- **自動暱稱識別**：支援 Twitch Tags 解析，能直接稱呼觀眾的「中文顯示名稱」。
- **AI 角色靈魂**：使用 Google Gemini API，並針對直播場景優化 Prompt，具備口頭禪與專屬稱呼功能。
- **VTS 動作連動**：根據 AI 回覆關鍵字自動觸發 VTube Studio 動作（如：揮手、愛心、生氣）。

## 📂 專案結構
- `rina_main.py`: 主程式入口，負責 Twitch 連線與異步任務管理 (Producer-Consumer Pattern)。
- `rina_ai_module.py`: AI 核心，處理 Gemini 請求與對話記憶。
- `rina_VTS_Audio.py`: 語音合成與 VTube Studio API 介面。
- `config.py`: 設定檔，包含 API 金鑰與頻道資訊。

## 🛠️ 安裝與設定

### 1. 安裝必要套件
```bash
pip install asyncio pygame edge-tts pyvts websockets google-generativeai
```

### 2. 設定金鑰
編輯 config.py 並填入必要的資訊：

- GEMINI_API_KEY

- TWITCH_TOKEN (由 [twitchtokengenerator.com](https://twitchtokengenerator.com/) 取得)

- TWITCH_CHANNEL

### 3. 啟動機器人
確保 VTube Studio 已開啟並啟用 API 功能（第一次啟動需在 VTS 視窗內點擊允許連線），然後執行：
```bash
py rina_main.py
```
