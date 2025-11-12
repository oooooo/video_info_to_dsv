# utils.py
import os
# import shutil  # 處理「檔案與資料夾的複製、刪除、壓縮、移動」等操作，比 os 更方便。


def list_files(directory, ext):
    """資料夾、指定副檔名"""
    try:
        # if not file.lower().endswith(AUDIO_EXTS):
        return [f for f in os.listdir(directory) if f.lower().endswith(ext)]
    except FileNotFoundError:
        print(f":: ❌ 錯誤: 找不到資料夾或檔案 '{directory}'")
        return []


def move_file(src, dst):
    """移動檔案到目標資料夾 快小"""
    os.rename(src, dst)
    # """移動檔案到目標資料夾 完整"""
    # shutil.move(src, dst)
    print(f":: --- 移動 '{src}' 到 '{dst}'")
    return dst
