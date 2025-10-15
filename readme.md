# 影片轉表單

透過 AI 分析介紹（收容狗狗）影片，從影片口述內容，整理出每隻狗狗的（指定）基本資料（如名字、年齡或性別、個性或行為等描述），
並產生一份類似 Excel 或 Google 試算表一樣的表單。

**流程**

1. 原始影片音訊抽出: 用開源軟體 FFmpeg 在本機執行
2. 音訊語音轉文字: 載入 whisper 在本機執行轉文字
3. 分析文字資訊（AI、指定欄位設定）: Google Gemini
4. 存為 CSV 資料表，方便分享管理: 在本機增修 CSV

**資料夾結構說明**


- `data/` 轉譯檔案暫放
  - `00_video/` 放置原始影片 (mov)
  - `01_audio/` 放置影片抽出的音訊 (wav)
  - `02_trans/` 放置音訊逐字稿 (srt)
  - `03_json/` 放置結構化文字資料 (json)
  - `04_csv/` 存入的 CSV 檔
  - `finish/` 處理後的檔案將移動到此資料夾 (不分類)
- `src/` 程式
- `.env.setting` 設定資料夾變數
- `.gitignore` 版控忽略設定
- `main.py` 主檔案
- `readme.md` 說明檔/本檔案
- `requirements.txt` 專案需求套件表

## 事前準備 (Tutorial for Mac)

1. 在本機安裝 FFmpeg 軟體：影片音訊抽出 (.mov ➜ .wav).

    FFmpeg 是一個開放原始碼的自由軟體，可以執行音訊和視訊多種格式的錄影、轉檔、串流功能。

    ```bash
    # 查看 ffmpeg 版本 （確認是否有安裝）
    ffmpeg -version
    ```
    ```bash
    # 用 Homebrew 下載安裝軟體 （需有 Homebrew）
    brew install ffmpeg
    ```
1. 主要使用 python 開發。 請確認安裝 python。
    ```bash
    # 查看電腦上 Python 版本 （確認是否有安裝）
    python3 --version

    # 查看 pip（Python 套件管理工具）的版本
    pip3 --version
    ```

    > Windows 前往 Python 官方網站下載最新版。 安裝過程中請**務必勾選：「Add Python 3.x to PATH」**。

## 安裝專案

### 1. 建立虛擬環境

下載後，在專案裡面建立 Python 虛擬環境（venv）。

> 虛擬環境是一個獨立的 Python 執行空間，專案需要用到的套件與工具都安裝在這個環境裡。
> Python 本身會在這個虛擬環境中執行，以確保程式在穩定、乾淨的環境下運作。

建立 Python 虛擬環境（venv）：
```shell
python3 -m venv venv
```

啟動此專案的虛擬環境：
```bash
source venv/bin/activate
```
啟動後 shell prompt 會出現 `(venv)` 前綴。

安裝 Python 套件（到虛擬環境）：
```bash

# Whisper（語音轉文字）# google-generativeai（分析文字）# python-dotenv（讀取 .env）
pip install git+https://github.com/openai/whisper.git google-generativeai python-dotenv
```

關閉虛擬環境指令
```bash
deactivate
```

### 2. AI 服務設定

這裡使用 Google 的 Gemini。

使用 AI 雲端服務，要申請 AI 的 API KEY (可能付費)。
API KEY 是一組帳號識別碼，為敏感資料，務必安全保管。

在專案根目錄手動建立 `.env` 檔案，並設定版控忽略 `.env`，
在 `.env` 放入你的 API Key 設定，格式如下（大寫、無空格、不需引號、斷行分隔）：

```bash
OPENAI_API_KEY=sk-你的金鑰
```

## 執行專案

1. 將影片放入 `data/00_video`
2. 開啟 `main.sh`
3. 開啟命令列 `ctrl`+ `` ` ``
4. 命令列輸入指令執行檔案
    ```bash
    sh main.sh
    ```

#### 運行 Whisper 時遇到問題

```bash
RuntimeError: Numpy is not available
```
你的 NumPy 版本太新，導致 PyTorch（還有 Whisper）無法正常運作。
Whisper 是「語音轉文字的模型」，它靠 PyTorch 做神經網路運算，PyTorch 又用 NumPy 做矩陣/數字運算。

1. 安裝套件（到虛擬環境）：指定的 numpy 版本,
    ```bash
    pip install "numpy<2"
    ```

2. 確認版本正確安裝，會回傳版本號

    ```bash
    python -c "import numpy; print(numpy.__version__)"
    ```

再次執行。
