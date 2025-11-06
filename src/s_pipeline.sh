#!/bin/bash
# s1_2_pipeline.sh extract / transcribe
MODE=$1
source .env.setting

# 影片副檔名
VIDEO_EXTS=(mp4 MOV mov avi mkv flv wmv)
# 音訊副檔名
AUDIO_EXTS=(wav m4a mp3 flac)

mkdir -p "$VIDEO_DIR" "$AUDIO_DIR" "$TRANS_DIR" "$FINISH_DIR" "$JSON_DIR" "$DSV_DIR" # 確保資料夾存在

case "$MODE" in
  extract)
    echo ":: 🙉 影片音訊抽出"
    SRC_DIR="$VIDEO_DIR"
    DST_DIR="$AUDIO_DIR"
    CMD='ffmpeg -hide_banner -v warning -i "$file" -ar 16000 -ac 1 "$DST_DIR/${name}.wav"'

    # # ===== 抓影片檔抽音訊 =====
    shopt -s nullglob
    file_list=()
    for ext in "${VIDEO_EXTS[@]}"; do
        file_list+=("$VIDEO_DIR"/*."$ext")
    done
    shopt -u nullglob
    ;;
  transcribe)
    echo ":: 🙊 語音轉文字 (較久)"
    SRC_DIR="$AUDIO_DIR"
    DST_DIR="$TRANS_DIR"
    # CMD='whisper "$file" --language Chinese --model medium --output_dir "$DST_DIR" --output_format srt'

    # 沒有 GPU 無法用 FP16:
    CMD='whisper "$file" --language Chinese --model medium --output_dir "$DST_DIR" --output_format srt --fp16 False'

    shopt -s nullglob
    file_list=()
    for ext in "${AUDIO_EXTS[@]}"; do
        file_list+=("$AUDIO_DIR"/*."$ext")
    done
    shopt -u nullglob
    ;;
  *)
    echo "用法: \"$0\" [extract|transcribe]"
    exit 1
    ;;
esac

# mkdir -p "$DST_DIR" "$FINISH_DIR"

if [ ${#file_list[@]} -eq 0 ]; then
  echo ":: ❌ 找不到可處理的檔案！"
  exit 1
fi

for file in "${file_list[@]}"; do
  filename=$(basename "$file")
  name="${filename%.*}"
  echo ":: ⏳ 處理中：\"$filename\""
  eval "$CMD"

  # 檢查上一個指令是否成功
  if [ $? -eq 0 ]; then
      mv "$file" "$FINISH_DIR"
      echo ":: 🚚 處理完成。移動 \"$filename\" 到 \"$FINISH_DIR\""
  else
      echo ":: ❌ 轉檔失敗"
  fi
done

echo ":: ✅ 轉譯檔案在 \"$DST_DIR\""
