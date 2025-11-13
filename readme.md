# Speak Sheet

在本機電腦作業。
協助觀察者把影片、口述音訊、文字紀錄等內容，依照事先定義好的欄位資料，抓取資訊，以資料表格式儲存，方便後續統整或分析。

情境舉例：

收容所動物很多，每隻動物的資料需一筆筆比對、手動建檔。
現在可以用手邊工具錄音錄影等方式，快速搜集資料，再將資料素材放入程式的指定資料夾 → 執行程式 → 產生整理好的表格資料，自動化一次產生多個動物檔案。


**流程**

- Step.1 原始影片音訊抽出: 用開源軟體 FFmpeg 在本機執行
- Step.2 音訊語音轉文字: 載入 whisper 在本機執行轉文字
- Step.3 分析文字資訊（AI、指定欄位設定）: Google Gemini
- Step.4 建立結構化的文字資料。
- Step.5 存為 DSV 資料表，方便分享管理: 在本機增修 DSV

**資料夾結構說明**

- `data/` 轉譯檔案暫放 (根據 `.env.setting` 的設定)
  - `01_video/` 放置影片檔
  - `02_audio/` 放置音訊檔
  - `03_trans/` 放置逐字稿檔案 (srt)
  - `04_json/` 運行過程產出結構化文字資料 (json)
  - `05_dsv/` 存入的 DSV 檔 (csv or tsv)
  - `finish/` 處理後的素材將移動到此資料夾 (不分類)
- `src/` 程式資料夾
- `.env.setting` 設定變數
- `.gitignore` 版控忽略
- `main.py` 主程式
- `readme.md` 說明檔/本檔案
- `requirements.txt` 專案需求套件表

以下說明是以 macOS 為操作環境所寫，Windows 使用者可依概念尋找對應指令，部分開發環境或工具（如 Python, FFmpeg）安裝方式有所差別。

## 事前準備

1. 自己的 Google Gemini 帳號 (AI 服務)
2. 安裝轉檔軟體 FFmpeg
3. 安裝程式執行環境 python

打開終端機：

### 在本機安裝 FFmpeg 軟體

FFmpeg 是一個開放原始碼的自由軟體，可以執行音訊和視訊多種格式的錄影、轉檔、串流功能。

終端機輸入指令：

```bash
ffmpeg -version
```

查看 ffmpeg 版本（確認是否有安裝），有安裝會顯示版本號。

(mac) 沒有安裝可用 Homebrew 下載安裝軟體 （需有 Homebrew）

```bash
brew install ffmpeg
```

### 確認有安裝 python (version >= 3.11)

終端機輸入指令：

查看電腦上 Python 版本（確認是否有安裝），有安裝會顯示版本號。
```bash
python3 --version
```

> 前往 Python 官方網站下載最新版。 Windows 安裝過程中請**務必勾選：「Add Python 3.x to PATH」**。


## 安裝專案

下載到電腦後

### 1. 建立虛擬環境

以終端機進入專案，建立 Python 虛擬環境（venv 資料夾）。
虛擬環境只需建立一次，之後僅「啟動」。

用系統的 python 在專案建立虛擬環境（venv）指令：

```shell
python3 -m venv venv
```

啟動專案的虛擬環境指令：

```bash
source venv/bin/activate
```
啟動後 shell prompt 會出現 `(venv)` 前綴。
啟動後 python、pip 指令都會指向 venv 的版本。

> 虛擬環境是一個獨立的 Python 執行空間，專案需要用到的套件與工具都安裝在這個環境裡。
> Python 本身會在這個虛擬環境中執行，以確保程式在穩定、乾淨的環境下運作。

升級虛擬環境中的 Python 輔助工具套件指令：

```bash
python -m pip install --upgrade pip setuptools wheel
```

安裝專案指定套件到虛擬環境指令：

```bash
pip install -r requirements.txt
```

若要關閉虛擬環境，輸入指令：

```bash
deactivate
```

### 2. AI 服務設定

使用 AI 雲端服務，要申請 AI 的 API KEY (可能付費) 請至官網。
API KEY 是一組帳號識別碼，為敏感資料，務必安全保管。

這裡使用 Google 的 Gemini （目前不須綁信用卡）。
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
1. 將影片放入 `data/01_video/` 資料夾
1. 執行主檔案，在命令列輸入指令：
    ```bash
    python main.py
    ```

    若要指定從哪個流程開始：

    - `1` 從 影片 開始處理（預設）
    - `2` 從 音訊 開始處理
    - `3` 從 字幕 開始處理
    - `4` 從 JSON 開始處理

    ```bash
    # 已有字幕檔，開始處理字幕檔：
    python main.py --s 3
    ```

#### 更多設定 `.env.setting`

表格 資料更新模式：
```bash
DSV_MODE=overwrite
# overwrite   新資料直接新增 / 同名新資料取代表格中的舊資料。
# log         新資料直接新增 / 同名僅通知有同名資料。
# modify_only 只取代同名資料
```

表格 檔案格式：
```bash
DSV_OUTPUT_FORMAT=tsv
# 設定輸出格式 tsv / csv
```

表格 檔案名稱：
```bash
DSV_FILENAME=table
```

## Note

issue：

- [ ] 音訊口齒不清是個問題
- [ ] 選字錯字 例如名字
- [x] 穿插內容（有指定名字回去補充）可以正確組合資訊


未來：

- 擷取圖片、短片
- 上傳圖床，建立連結
- 外部上架流程：填入檔案、確認資訊、確認圖片、上下架
- line text -> google sheet（無伺服器）
- line 語音/影片 -> google sheet
