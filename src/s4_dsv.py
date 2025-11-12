import os
import csv
import json
from dotenv import load_dotenv
from . import _dir
from . import _utils


# 載入 .env
load_dotenv(".env.setting")

MODE = os.getenv("DSV_MODE")
# MODE = "overwrite"  # overwrite / log / modify_only

OUTPUT_FORMAT = os.getenv("DSV_OUTPUT_FORMAT")
# OUTPUT_FORMAT = "csv"   # tsv / csv

DSV_FILENAME = os.getenv("DSV_FILENAME")

# 根據輸出格式設定副檔名與分隔符
if OUTPUT_FORMAT == "tsv":
    DELIMITER = "\t"
    EXT = ".tsv"
else:
    DELIMITER = ","
    EXT = ".csv"


def load_dsv(path):
    """讀取 DSV 檔"""
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


def export_dsv():
    """將 JSON 轉成 DSV 檔案"""
    DSV_FILE = os.path.join(_dir.DSV_DIR, f"{DSV_FILENAME}{EXT}")
    print(f":: 🐵 存入 DSV:  {DSV_FILENAME}.{OUTPUT_FORMAT}, MODE: {MODE}")

    # 初始化 DSV 資料 ----------
    existing_data, headers = load_dsv(DSV_FILE)

    # 處理來源 ----------
    pending = _utils.list_files(_dir.JSON_DIR, ".json")
    if not pending:
        print(f":: ⚠️ {_dir.JSON_DIR} 沒有待處理檔案")
        return

    # 處理 data----------
    for file in pending:
        filepath = os.path.join(_dir.JSON_DIR, file)

        # 讀取內容
        print(f":: process {file} ➜ DSV")

        try:
            # load json
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError:
            print(f":: ⚠️ {file} JSON 解析失敗。")
            continue
        except Exception as e:
            print(f":: ❌ {file} 發生其他錯誤: {e}")
            continue

        # 整合筆數
        for record in data:
            # 添加檔名
            record["file_name"] = file

            # 1. 檢查 record 是否有新欄位（:: 更新 header）
            for field in record.keys():
                # 比對原標題
                if field not in headers:
                    headers.append(field)   # 新欄位加到最後

            # 2. 確保 record 都能對應標題欄位，缺的補上值
            for field in headers:
                if field not in record:
                    record[field] = None  # 或 "" or 0

            # 整合 existing_data 資料 以姓名識別
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

        # 來源檔案處理完，移動至 FINISH_DIR  ----------
        _utils.move_file(filepath, os.path.join(_dir.FINISH_DIR, file))

    # 寫回 DSV ----------
    # os.makedirs(os.path.dirname(DSV_FILE), exist_ok=True)
    with open(DSV_FILE, "w", newline="", encoding="utf-8") as f:
        # writer = csv.DictWriter(f, headers)
        writer = csv.DictWriter(f, headers, delimiter=DELIMITER)
        writer.writeheader()  # 將標題列寫入文件（第一行）
        for row in existing_data.values():
            writer.writerow(row)

    print(f":: ✅ DSV 完成: {DSV_FILE}")
