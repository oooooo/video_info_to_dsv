# Video Info To DSV

將影片、語音、文字資料，分析並轉為「表格資料」檔案保存，表格的欄位可自定義。最後產生一份類似 Excel 或 Google 試算表一樣的表單。

情境舉例：

收容所狗狗很多，每隻狗的資料需一筆筆比對、建檔。
現在可以拍攝一段影片，或一段口頭說明錄音、或既有文字檔，用手邊工具快速產生每隻狗狗的資料後，將素材放入程式的指定資料夾 → 執行程式 → 產生整理好的表格資料，自動化一次建立多個動物檔案。

**流程**

- Step.1 原始影片音訊抽出: 用開源軟體 FFmpeg 在本機執行
- Step.2 音訊語音轉文字: 載入 whisper 在本機執行轉文字
- Step.3 分析文字資訊（AI、指定欄位設定）: Google Gemini
- Step.4 存為 DSV 資料表，方便分享管理: 在本機增修 DSV

**資料夾結構說明**

- `data/` 轉譯檔案暫放
  - `00_video/` 放置影片檔
  - `01_audio/` 放置音訊檔
  - `02_trans/` 放置逐字稿檔案 (srt)
  - `03_json/` 運行過程產出結構化文字資料 (json)
  - `04_dsv/` 存入的 DSV 檔 (csv or tsv)
  - `finish/` 處理後的素材將移動到此資料夾 (不分類)
- `src/` 程式資料夾
- `.env.setting` 設定變數
- `.gitignore` 版控忽略
- `main.py` 主程式
- `readme.md` 說明檔/本檔案
- `requirements.txt` 專案需求套件表

**主要使用套件**

- Whisper（語音轉文字）`pip install git+https://github.com/openai/whisper.git`
- google-generativeai（分析文字）`pip install google-generativeai`
- python-dotenv（讀取 .env）`pip install python-dotenv`

以下說明是以 macOS 為操作環境所寫，Windows 使用者可依概念尋找對應指令，部分開發環境或工具（如 Python, FFmpeg）則是用不同的安裝方式。

## 事前準備

打開終端機：

1. 在本機安裝 FFmpeg 軟體：影片音訊抽出 (.mov ➜ .wav).

    FFmpeg 是一個開放原始碼的自由軟體，可以執行音訊和視訊多種格式的錄影、轉檔、串流功能。

    終端機輸入指令：

    ffmpeg 版本 （確認是否有安裝）
    ```bash
    ffmpeg -version
    ```
    有安裝會顯示版本號。

    (mac) 沒有安裝可用 Homebrew 下載安裝軟體 （需有 Homebrew）
    ```bash
    brew install ffmpeg
    ```

1. 主要使用 python 開發。 請確認有安裝 python (version >= 3.11)。

    終端機輸入指令：

    查看電腦上 Python 版本 （確認是否有安裝）
    ```bash
    python3 --version
    ```
    查看 pip（Python 套件管理工具）的版本
    ```bash
    pip3 --version
    ```
    以上有安裝會顯示版本號。

    > Windows 前往 Python 官方網站下載最新版。 安裝過程中請**務必勾選：「Add Python 3.x to PATH」**。

1. 自己的 Google Gemini 帳號 (AI 服務設定)

## 安裝專案


### 1. 建立虛擬環境

終端機進入專案，建立 Python 虛擬環境（venv）。
建立 Python 虛擬環境（venv），指令：
```shell
python3 -m venv venv
```

啟動此專案的虛擬環境：
```bash
source venv/bin/activate
```
啟動後 shell prompt 會出現 `(venv)` 前綴。

> 虛擬環境是一個獨立的 Python 執行空間，專案需要用到的套件與工具都安裝在這個環境裡。
> Python 本身會在這個虛擬環境中執行，以確保程式在穩定、乾淨的環境下運作。

安裝 Python 套件（到虛擬環境）：
```bash
pip install -r requirements.txt
```

若要關閉虛擬環境：
```bash
deactivate
```

### 2. AI 服務設定

使用 AI 雲端服務，要申請 AI 的 API KEY (可能付費) 請至官網。
API KEY 是一組帳號識別碼，為敏感資料，務必安全保管。

這裡使用 Google 的 Gemini （目前不須信用卡）。
> 到 https://aistudio.google.com/app/apikey
> 登入 Google 帳號並產生 API 金鑰
> 會得到一組 API key

在專案根目錄手動建立 `.env` 檔案 (版本控制已忽略 `.env`，建好後檔名應為暗色，代表不被版控的狀態)，在 `.env` 放入下面設定：

```bash
OPENAI_API_KEY=你的金鑰
```
然後將「你的金鑰」部分替換成你申請好的 API KEY，儲存。

## 執行專案

1. 啟動專案的虛擬環境

    開啟命令列 `ctrl`+ `` ` `` 輸入指令
    ```bash
    source venv/bin/activate
    ```
1. 將影片放入 `data/00_video/` 資料夾
1. 執行主檔案，在命令列輸入指令：
    ```bash
    sh main.sh
    ```

    若要指定從哪個流程開始：

    - `1` 轉音訊開始（預設）
    - `2` 轉字幕開始
    - `3` 轉 JSON 開始
    - `4` 存入 DSV.

    ```bash
    # 已有字幕檔，從轉 JSON 開始
    sh main.sh 3
    ```
#### 設定

開啟檔案： .env.setting

```bash
# 表格資料更新模式：
DSV_MODE=overwrite
# overwrite   新資料直接新增 / 同名新資料取代表格中的舊資料。
# log         新資料直接新增 / 同名僅通知有同名資料。
# modify_only 只取代同名資料

# 表格檔案格式：
DSV_OUTPUT_FORMAT=tsv
# 設定輸出格式 tsv / csv
```

#### 運行 Whisper（Step.2）時遇到問題

```bash
.....
RuntimeError: Numpy is not available
```
你的 NumPy 版本不合，導致 PyTorch（還有 Whisper）無法正常運作。
Whisper 是「語音轉文字的模型」，它靠 PyTorch 做神經網路運算，PyTorch 又用 NumPy 做矩陣/數字運算。

安裝前確認虛擬環境 (venv) 已啟動 `source venv/bin/activate`。

1. 安裝套件（到虛擬環境）：指定的 numpy 版本,
    ```bash
    pip install "numpy<2"
    ```

2. 確認版本正確安裝，會回傳版本號

    ```bash
    python -c "import numpy; print(numpy.__version__)"
    ```

再次執行。

## Note

待新增功能：

- 擷取圖片、短片
- 上傳圖床，建立連結
- 外部上架流程：填入檔案、確認資訊、確認圖片、上下架
