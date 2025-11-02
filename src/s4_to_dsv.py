import os
import sys
import csv
import json
from dotenv import load_dotenv
from utils import list_files, move_file

# ---------- 設定 ----------

MODE = "overwrite"  # overwrite / log / modify_only
OUTPUT_FORMAT = "csv"   # tsv / csv
print(f":: 🐵 存入 DSV, MODE: {MODE}, FORMAT: {OUTPUT_FORMAT}")


# 載入 .env
load_dotenv(".env.setting")

# 目錄
JSON_DIR = os.getenv("JSON_DIR")
DSV_DIR = os.getenv("DSV_DIR")
FINISH_DIR = os.getenv("FINISH_DIR")
# 根據輸出格式設定副檔名與分隔符
if OUTPUT_FORMAT == "tsv":
    DELIMITER = "\t"
    EXT = ".tsv"
else:
    DELIMITER = ","
    EXT = ".csv"

DSV_FILE = os.path.join(DSV_DIR, f"new{EXT}")


def load_dsv(path):
    data = {}
    headers = []
    # 檢查檔案是否存在
    if not os.path.exists(path):
        # 檔案不存在，回傳空的資料和標題
        return data, headers

    # 讀取 DSV 檔
    with open(path, "r", newline="", encoding="utf-8") as f:
        # reader = csv.DictReader(f) # csv
        reader = csv.DictReader(f, delimiter=DELIMITER)  # 改成 Tab
        # 讀取標題
        headers = reader.fieldnames or []
        # 讀取資料
        for row in reader:
            # 取得名稱
            name = row.get("name")
            # 將資料存入字典
            if name:
                # 檢查名稱是否重複
                data[name] = row
    return data, headers


# ---------- 初始化 DSV 資料 ----------
existing_data, headers = load_dsv(DSV_FILE)

# ---------- 處理來源 ----------
pending_files = list_files(JSON_DIR, ".json")
if not pending_files:
    print(":: ⚠️ 沒有待處理檔案，跳過。")
    sys.exit(0)

# ---------- 處理 data----------
for file_name in pending_files:
    file_path = os.path.join(JSON_DIR, file_name)

    # 讀取內容
    print(f":: ⏳ 處理中：{file_name} ➜ DSV")

    try:
        # load json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    except json.JSONDecodeError:
        print(f":: ⚠️ {file_name} JSON 解析失敗。")
        continue
    except Exception as e:
        print(f":: ❌ {file_name} 發生其他錯誤: {e}")
        continue

    # 整合筆數
    for record in data:
        # 添加檔名
        record["file_name"] = file_name

        # 1. 檢查 record 是否有新欄位（:: 更新 header）
        for field in record.keys():
            # 比對原標題
            if field not in headers:
                headers.append(field)   # 新欄位加到最後

        # 2. 確保 record 都能對應標題欄位，缺的補上值
        for field in headers:
            if field not in record:
                record[field] = None  # 或 "" or 0

        # 整合 existing_data 資料
        name = record.get("name")

        # 根據模式整合資料

        if MODE == "overwrite":
            # 直接新增/覆寫 資料
            existing_data[name] = record
        elif MODE == "log":
            if name in existing_data:
                # 重複資料 印出
                print(f":: 印出重複：{name}")
            else:
                # 新資料
                existing_data[name] = record
                print(f":: 新增：{name}")
        elif MODE == "modify_only":
            if name in existing_data:
                existing_data[name] = record
                print(f":: 覆寫：{name}")
            else:
                # 新資料 不新增
                print(f":: 未找到 {name}")

    # ---------- 來源檔案處理完，移動至 FINISH_DIR  ----------
    move_file(file_path, FINISH_DIR)
    print(f":: 🚚 處理完畢，移動 {file_name} 到 FINISH_DIR")

# ---------- 寫回 DSV ----------
os.makedirs(os.path.dirname(DSV_FILE), exist_ok=True)
with open(DSV_FILE, "w", newline="", encoding="utf-8") as f:
    # writer = csv.DictWriter(f, headers)
    writer = csv.DictWriter(f, headers, delimiter=DELIMITER)
    writer.writeheader()  # 將標題列寫入文件（第一行）
    for row in existing_data.values():
        writer.writerow(row)

print(f":: ✅ DSV 更新完成: {DSV_FILE}")
