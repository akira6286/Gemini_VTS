# 🐾 Rina Twitch Bot (凜奈) - VTS 連動 AI 機器人

這是一個結合了 **Gemini AI** 記憶功能、**Edge-TTS** 語音合成，以及 **VTube Studio** 動作連動的 Twitch 聊天室機器人。

## 🌟 功能亮點
- **AI 智能對話**：使用 Google Gemini API，具備短期對話記憶，能根據上下文回覆。
- **名稱與貼圖辨識**：優化過濾 Twitch 貼圖代碼，並能精確分辨發言者姓名。
- **語音系統**：透過 Edge-TTS 提供自然的人聲回覆，並與語音播放同步。
- **VTS 動作連動**：根據 AI 回覆中的關鍵字，自動觸發 VTube Studio 的快捷動作（如：揮手、愛心、生氣）。
- **模組化設計**：程式碼結構清晰，易於維護與擴充功能。

## 📂 專案結構
- `rina_main.py`: 主程式入口，處理 Twitch IRC 連線。
- `ai_module.py`: AI 邏輯模組，處理對話記憶與 Gemini 請求。
- `vts_audio.py`: 語音播放與 VTube Studio 動作觸發。
- `config.py.example`: 設定檔範例（使用前請更名為 `config.py`）。

## 🛠️ 安裝與設定

### 1. 複製專案
將本倉庫的所有檔案下載或複製到本地資料夾。

### 2. 安裝必要套件
在終端機執行以下指令：
```bash
pip install asyncio requests pygame edge-tts pyvts websockets
```

### 3. 設定金鑰
找到 config.py.example 檔案。

將其更名為 config.py。

填入你的 GEMINI_API_KEY 與 TWITCH_TOKEN。

### 4. 啟動機器人
確保 VTube Studio 已開啟並啟用 API 功能，然後執行：
```bash
py rina_main.py
```
🎮 使用說明
機器人會監控你的 Twitch 頻道聊天室。

當聊天室有新訊息時，機器人會透過 Gemini 生成回應。

如果回應中包含特定關鍵字（如「你好」），VTS 模型會自動觸發對應動作。

