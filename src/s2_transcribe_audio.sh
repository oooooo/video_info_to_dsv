#!/bin/bash

echo ":: 🙊 開始 語音辨識...(會較久)"

# 匯入環境變數
source .env.setting
# 目錄
echo ":: 📂 AUDIO_DIR: $AUDIO_DIR"
echo ":: 📂 TRANS_DIR: $TRANS_DIR"
echo ":: 📂 FINISH_DIR: $FINISH_DIR"

mkdir -p "$TRANS_DIR"
shopt -s nullglob
file_list=("$AUDIO_DIR"/*.[wW][aA][vV]) # 影片檔案陣列

if [ ${#file_list[@]} -eq 0 ]; then
  echo ":: ❌ 找不到檔案！"
  exit 1
fi

# .wav ➜ .srt
for file in "${file_list[@]}"; do
  filename=$(basename "$file")

  echo ":: ⏳ 處理中：$filename ➜ .srt"
  whisper "$file" \
    --language Chinese \
    --model medium \
    --output_dir "$TRANS_DIR" \
    --output_format srt

  # 轉完後移動影片到 finish
  mv "$file" "$FINISH_DIR"
  echo ":: 🚚 已移動 \"$filename\" 到 \"$FINISH_DIR\""

done

echo ":: ✅ 完成：逐字稿在 $TRANS_DIR"
