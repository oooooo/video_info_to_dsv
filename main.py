import argparse

# from s1_audio import extract_audio
# from s2_str import transcribe_audio
# from s3_json import srt_to_json
# from s4_dsv import export_dsv
from src.s1_audio import extract_audio
from src.s2_str import transcribe_audio
from src.s3_json import srt_to_json
from src.s4_dsv import export_dsv

# -------------------------
# 解析命令列
# -------------------------

parser = argparse.ArgumentParser()
parser.add_argument(
    "--s", choices=["1", "2", "3", "4"], default="1", help="選擇從 1影片 2音檔 3字幕 4 json 開始處理")
parser.add_argument(
    "--add_txt", action="store_true", help="是否保留純文字檔")

args = parser.parse_args()


# -------------------------
# 主流程
# -------------------------
if args.s == "1":
    extract_audio()
    transcribe_audio(args.add_txt)
    srt_to_json()
    export_dsv()
elif args.s == "2":
    transcribe_audio(args.add_txt)
    srt_to_json()
    export_dsv()
elif args.s == "3":
    srt_to_json()
    export_dsv()
elif args.s == "4":
    export_dsv()


print(":: 🎉 所有檔案處理完成")
