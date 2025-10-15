import sys
import os
import shutil  # 處理「檔案與資料夾的複製、刪除、壓縮、移動」等操作，比 os 更方便。
import json
import google.generativeai as genai
from dotenv import load_dotenv

# ---------- 設定 ----------

print(f":: 🙈 開始 結構化文字訊息...")

# 載入 .env
load_dotenv(".env.setting")
load_dotenv()

# 目錄
TRANS_DIR = os.getenv("TRANS_DIR")
JSON_DIR = os.getenv("JSON_DIR")
FINISH_DIR = os.getenv("FINISH_DIR")

print(f":: 📂 TRANS_DIR: {TRANS_DIR}")
print(f":: 📂 JSON_DIR: {JSON_DIR}")
print(f":: 📂 FINISH_DIR: {FINISH_DIR}")

# 金鑰
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 提示稿
speech2 = """
你是一個資料解析助手，任務是將字幕檔 (.srt) 轉換成 JSON 陣列。

字幕檔內容是介紹一隻或多隻動物。
每隻動物都有一段連續字幕描述，依序介紹。

請輸出唯一一個 JSON 陣列，每個元素對應一隻動物。

每個物件結構如下，以下為範例（僅作為格式參考）：
[
  {
    "name": "小黑",
    "species": "狗",
    "gender": "母",
    "age": 10,
    "health_condition": "良好",
    "body_features": "超過20公斤的中型犬",
    "interaction_with_humans": "親人溫和",
    "interaction_with_other_animals": "親狗親貓",
    "srt": [
      "00:00:00,000 --> 00:00:04,000 這是小黑,牠是一隻山區放養的母狗",
      "00:00:06,000 --> 00:00:09,000 牠大概快十歲了",
      "00:00:10,000 --> 00:00:11,000 最近已經結紮",
      "00:00:12,000 --> 00:00:15,000 牠是超過20公斤的中型犬",
      "00:00:16,000 --> 00:00:21,000 現在健康狀況良好",
      "00:00:24,000 --> 00:00:27,000 然後對陌生人親近溫和",
      "00:00:27,000 --> 00:00:29,000 也親狗貓",
      "00:00:30,000 --> 00:00:33,000 適合家庭生活"
    ]
  }
]

請完全遵照上述格式與 key 命名輸出。

規則：
- 所有 key 都要出現。
- 若資訊缺少，填入 null 或空字串 ""。
- srt 是陣列，內容為該動物段落的字幕（含時間碼）。
- 僅輸出純 JSON，不要文字說明。
- 若字幕中有多隻動物，請依序分開成多個物件。

字幕內容如下：
"""

# 建立一個空字典來存放所有檔案的處理結果
all_results = {}  # {srt: {...}, ... }

# ---------- 初始化 genai ----------
genai.configure(api_key=GEMINI_API_KEY)

# # 列出可用模型
# models = genai.list_models()
# for m in models:  # ✅ 直接迭代 generator
#     print(f":: {m.name}")

# 建立 Gemini 模型
model = genai.GenerativeModel("gemini-2.0-flash")

# ---------- 處理來源 ----------
try:
    file_list = os.listdir(TRANS_DIR)
except FileNotFoundError:
    print(f":: ❌ 錯誤: 找不到資料夾 '{TRANS_DIR}'，請確認路徑是否正確。")
    sys.exit(1)

# 待處理檔案
pending_files = [f for f in file_list if f.endswith(".srt")]
if not pending_files:
    print(":: ⚠️ 沒有 待處理檔案，跳過。")
    sys.exit(0)

# 處理
for file_name in pending_files:
    file_path = os.path.join(TRANS_DIR, file_name)

    # 進行分析
    print(f":: ⏳ 處理中： {file_name} ➜ JSON")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 提示詞（Prompt）
        prompt = f"""{speech2}
        {text}
        請只輸出 JSON 陣列。
        """

        # 以提示詞（Prompt）呼叫 Gemini
        response = model.generate_content(prompt)
        response_text = response.text
        cleaned_text = response_text.replace(
            "```json", "").replace("```", "").strip()
        # print(':: cleaned_text', cleaned_text)
        all_results[file_name] = json.loads(cleaned_text)
        # print(':: all_results', all_results)
        # <array> [{animal data}, {}, ...]

    except json.JSONDecodeError:
        print(
            f":: ⚠️ 警告: 檔案 '{file_name}' 的回應不是有效的 JSON 格式，跳過此檔案。{response.text}")
        all_results[file_name] = f":: ❌ 錯誤: 無法解析回應為 JSON。原始回應：{response.text}"

    except Exception as e:
        print(f":: ❗️ 處理 {file_name} 時發生錯誤: {e} ---")

    # ---------- 來源檔案處理完，移動至 FINISH_DIR  ----------
    dst_path = os.path.join(FINISH_DIR, file_name)
    shutil.move(file_path, dst_path)
    print(f":: 🚚 已移動 {file_name} 到 {FINISH_DIR}")

# ---------- 存為 JSON ----------
for file_name, data in all_results.items():
    base_name = os.path.splitext(file_name)[0]
    json_name = f"{base_name}.json"
    output_path = os.path.join(JSON_DIR, json_name)

    # 將所有結果寫入一個 JSON 檔案
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            # 以 JSON 格式寫入檔案(寫入,檔案,編碼,縮排)
        print(f":: ✅ 所有動物資訊已成功儲存至檔案：'{output_path}'")
    except Exception as e:
        print(f":: ❌ 錯誤: {data} 無法寫入 JSON 檔案。原因：{e}")
