import sys
import os
import shutil
import json
import csv
from dotenv import load_dotenv

# ---------- 設定 ----------

print(':: 🐵 存入 CSV')

# 載入 .env
load_dotenv(".env.setting")

# 目錄
JSON_DIR = os.getenv("JSON_DIR")
CSV_DIR = os.getenv("CSV_DIR")
FINISH_DIR = os.getenv("FINISH_DIR")
CSV_FILE = CSV_DIR+"/new.csv"

# 目錄
print(f":: 📂 JSON_DIR: {JSON_DIR}")
print(f":: 📂 CSV_FILE: {CSV_FILE}")
print(f":: 📂 FINISH_DIR: {FINISH_DIR}")

MODE = "overwrite"  # overwrite / log / modify_only

# ---------- 初始化 CSV ----------
headers = None
existing_data = {}

if not os.path.exists(CSV_FILE):
    print(':: 沒 CSV → 建立空檔')
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[])  # 建立含標題列的空白 CSV
        writer.writeheader()

with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
    print(':: 讀取 CSV 檔案')
    reader = csv.DictReader(f)
    headers = reader.fieldnames or []
    # print(':: headers:', headers)

    for row in reader:
        existing_data[row.get("name")] = row

    # print(':: existing_data:', existing_data)

# ---------- 處理來源 ----------
try:
    file_list = os.listdir(JSON_DIR)
except FileNotFoundError:
    print(f":: ❌ 錯誤: 找不到資料夾 '{JSON_DIR}'，請確認路徑是否正確。")
    sys.exit(1)

# 待處理檔案
pending_files = [f for f in file_list if f.endswith(".json")]
if not pending_files:
    print(":: ⚠️ 沒有 待處理檔案，跳過。")
    sys.exit(0)

# 處理
for file_name in pending_files:
    file_path = os.path.join(JSON_DIR, file_name)

    # 讀取內容
    print(f":: ⏳ 處理中： {file_name} ➜ CSV")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f":: ❌ 無法解析 JSON：{file_name}")
        continue
    except Exception as e:
        print(f":: ⚠️ 無法讀取 {file_name}：{e}")
        continue

    if not isinstance(data, list) or not data:
        print(f":: ⚠️ {file_name} 為空或不是 list，略過。")
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
        print(':: MODE:', MODE)

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
    dst_path = os.path.join(FINISH_DIR, file_name)
    shutil.move(file_path, dst_path)
    print(f":: 🚚 已移動 {file_name} 到 {FINISH_DIR}")

# ---------- 寫回 CSV ----------
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()  # 將標題列寫入文件（第一行）
    for row in existing_data.values():
        writer.writerow(row)

print(f":: ✅ 批次處理完成，資料已更新到 {CSV_FILE}")
