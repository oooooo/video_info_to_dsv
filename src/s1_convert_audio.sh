#!/bin/bash

echo ":: 🙉 開始 音訊抽出..."

# 匯入環境變數
source .env.setting
# 目錄
echo ":: 📂 VIDEO_DIR: $VIDEO_DIR"
echo ":: 📂 AUDIO_DIR: $AUDIO_DIR"
echo ":: 📂 FINISH_DIR: $FINISH_DIR"

# 建立資料夾
mkdir -p "$AUDIO_DIR"

# 避免沒檔案時 glob 展開出錯
shopt -s nullglob
file_list=("$VIDEO_DIR"/*.[mM][oO][vV]) # 影片檔案陣列

if [ ${#file_list[@]} -eq 0 ]; then
  echo ":: ❌ 找不到檔案！"
  exit 1
fi

# .mov ➜ .wav
for file in "${file_list[@]}"; do
  filename=$(basename "$file")
  name="${filename%.*}"

  echo ":: ⏳ 處理中：$filename ➜ $name.wav"
  ffmpeg -hide_banner -v warning -i "$file" -ar 16000 -ac 1 "$AUDIO_DIR/${name}.wav"

  # 轉完後移動影片到 finish
  mv "$file" "$FINISH_DIR"
  echo ":: 🚚 已移動 \"$filename\" 到 \"$FINISH_DIR\""
done

echo ":: ✅ 完成：音訊檔在 $AUDIO_DIR"
