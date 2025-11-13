
import torch
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import whisper
from . import _dir
from . import _utils


# 支援副檔名
AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".flac")

# 每段 5 分鐘
SEGMENT_MS = 5 * 60 * 1000

# Whisper 模型
# model = whisper.load_model("medium")  # 可改 medium/base/small


def load_whisper_model(model_size="medium"):
    """
    載入 Whisper 模型，根據環境自動判斷是否啟用 GPU / FP16。
    """
    if torch.cuda.is_available():
        print(":: --- 偵測到 GPU，可使用 FP16 模式")
        model = whisper.load_model(model_size).to("cuda")
        use_fp16 = True
    else:
        print(":: --- 未偵測到 GPU，自動切換至 CPU 模式 (fp16=False)")
        model = whisper.load_model(model_size, device="cpu")
        use_fp16 = False
    return model, use_fp16


def segments_to_srt(segments, srt_path):
    """處理音訊片段 SRT"""

    def format_timestamp(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")


def transcribe_audio(add_txt=False):
    print(":: 🙉 音訊轉字幕：")
    """音檔分段 + Whisper 轉錄 + 生成 SRT"""

    model, use_fp16 = load_whisper_model()

    pending = _utils.list_files(_dir.AUDIO_DIR, AUDIO_EXTS)
    if not pending:
        print(f":: ⚠️ {_dir.AUDIO_DIR} 沒有待處理檔案")
        return

    for file in pending:
        filepath = os.path.join(_dir.AUDIO_DIR, file)
        filename = os.path.splitext(file)[0]

        print(f":: process {file}")
        # 載入音訊檔，變成可以在 Python 裡操作的音訊物件
        audio = AudioSegment.from_file(filepath)
        segments_all = []

        # 音訊分段
        for i in range(0, len(audio), SEGMENT_MS):
            # len(audio) 音檔的長度（毫秒, ms）
            # 從 i 取到 i+SEGMENT_MS 毫秒。
            seg = audio[i:i+SEGMENT_MS]
            seg_file = "temp_seg.wav"
            seg_path = os.path.join(_dir.AUDIO_DIR, seg_file)
            seg.export(seg_path, format="wav")

            # 給 Whisper 轉錄
            # result = model.transcribe(seg_file, language="Chinese")
            result = model.transcribe(
                seg_path, language="Chinese", fp16=use_fp16)

            """ result = {
                "text": "你好 我是測試",
                "segments": [
                    {"start":0.0, "end":3.2, "text":"你好"},
                    {"start":3.2, "end":6.5, "text":"我是測試"}
                ],
                "language": "zh"
            }
            """
            segments_all.extend(result["segments"])
            # extend() 把可迭代物件的每個元素「拆開」、「逐個加入」 list
            os.remove(seg_path)

        # 生成 SRT 字幕
        srt_path = os.path.join(_dir.TRANS_DIR, f"{filename}.srt")
        segments_to_srt(segments_all, srt_path)
        # print(f":: SRT 完成 {srt_path}")

        # 選擇性生成 TXT （in TRANS_DIR）
        if add_txt:
            txt_path = os.path.join(_dir.TRANS_DIR, f"{filename}.txt")
            full_text = "\n".join([seg["text"] for seg in segments_all])
            # 寫入檔案 (覆蓋)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text.strip())
            # print(f":: TXT 完成 {txt_path}")

        # 處理完移動檔案
        _utils.move_file(filepath, os.path.join(_dir.FINISH_DIR, file))


def srt_to_txt(srt_dir):
    """
    將 TRANS_DIR 下的所有 SRT 轉成 TXT
    srt_dir: SRT 所在資料夾
    """
    for file in os.listdir(srt_dir):
        if not file.lower().endswith(".srt"):
            continue
        srt_path = os.path.join(srt_dir, file)
        txt_path = os.path.join(srt_dir, f"{os.path.splitext(file)[0]}.txt")
        with open(srt_path, "r", encoding="utf-8") as f:
            # 列表生成式 [表達式 for 變數 in 可迭代物件 if 條件]
            # 不是有 "-->" 那行 / 不是空行 line.strip() / 這行不是 全數字
            lines = [
                line.strip()
                for line in f.readlines()
                if "-->" not in line and line.strip() and not line.isdigit()
            ]

        # 寫入/覆蓋
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(" ".join(lines))
        print(f":: 從 SRT 生成 TXT {txt_path}")
