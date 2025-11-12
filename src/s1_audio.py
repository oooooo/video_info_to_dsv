
import os
from dotenv import load_dotenv
import subprocess
from . import _dir
from . import _utils


# 支援副檔名
VIDEO_EXTS = (".mp4", ".MOV", ".mov", ".avi", ".mkv", ".flv", ".wmv")


def extract_audio():
    print(":: 🙉 影片音訊抽出：")
    """影片抽音訊"""
    pending = _utils.list_files(_dir.VIDEO_DIR, VIDEO_EXTS)
    if not pending:
        print(f":: ⚠️ {_dir.VIDEO_DIR} 沒有待處理檔案")
        return

    for file in pending:
        filepath = os.path.join(_dir.VIDEO_DIR, file)
        filename = os.path.splitext(file)[0]
        audio_path = os.path.join(_dir.AUDIO_DIR, f"{filename}.wav")
        print(f":: process {file}")
        # 在 python 中執行系統命令
        subprocess.run([
            "ffmpeg",                # 呼叫 ffmpeg
            "-y",                    # 覆蓋輸出檔案（不問 y/n）
            "-hide_banner",          # 輸出隱藏開頭的版本資訊
            "-loglevel", "warning",  # 只顯示警告與錯誤
            "-i", filepath,          # 輸入檔案路徑
            "-ar", "16000",          # 音訊取樣率 16kHz（Whisper 要求）
            "-ac", "1",              # 音軌數 單聲道（mono）
            audio_path               # 輸出路徑
        ])
        # 處理完移動檔案
        _utils.move_file(filepath, os.path.join(_dir.FINISH_DIR, file))
