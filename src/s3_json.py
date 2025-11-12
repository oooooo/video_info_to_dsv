import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from . import _dir
from . import _utils

load_dotenv()

# GEMINI 金鑰
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GEMINI INIT
genai.configure(api_key=GEMINI_API_KEY)

# # 列出可用模型
# models = genai.list_models()
# for m in models:  # 直接迭代 generator
#     print(f":: {m.name}")

# Gemini 模型
model = genai.GenerativeModel("gemini-2.0-flash")

# json 提示稿
josn_prompt = """
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


def srt_to_json():
    print(":: 🙉 字幕換 JSON：")
    """處理 SRT to JSON (AI)"""
    pending = _utils.list_files(_dir.TRANS_DIR, ".srt")
    if not pending:
        print(f":: ⚠️ {_dir.TRANS_DIR} 沒有待處理檔案")
        return

    result = {}

    # 依序分析
    for file in pending:
        print(f":: process {file}")
        filepath = os.path.join(_dir.TRANS_DIR, file)
        try:
            # load srt
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            # 提示詞（Prompt）
            prompt = f"""{josn_prompt}
            {text}
            請只輸出 JSON 陣列。
            """

            # 呼叫 Gemini 分析
            response = model.generate_content(prompt)
            response_text = response.text
            cleaned_text = response_text.replace(
                "```json", "").replace("```", "").strip()
            result[file] = json.loads(cleaned_text)  # [{data}, {}]

            # 移至 FINISH_DIR
            _utils.move_file(filepath, os.path.join(_dir.FINISH_DIR, file))

        except json.JSONDecodeError:
            print(f":: ⚠️ {file} JSON 解析失敗： {response.text}")
            result[file] = f":: ❌ JSON 解析失敗。"  # 寫入資料
            continue
        except Exception as e:
            print(f":: ❌ {file} 發生其他錯誤: {e}")
            continue

    # 寫入 JSON 檔
    for file, data in result.items():
        base_name = os.path.splitext(file)[0]
        json_name = f"{base_name}.json"
        output_path = os.path.join(_dir.JSON_DIR, json_name)

        try:
            with open(output_path, "w", encoding="utf-8") as json_file:
                # 將 Python 物件 轉成 JSON 並寫入 JSON 檔案
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f":: build {json_name}")
        except Exception as e:
            print(f":: ❌ 錯誤: {data} 無法寫入 JSON 檔案。原因：{e}")
