#!/bin/bash
# s1_2_pipeline.sh extract / transcribe
MODE=$1
source .env.setting

case "$MODE" in
  extract)
    echo ":: 🙉 影片音訊抽出"
    SRC_DIR="$VIDEO_DIR"
    DST_DIR="$AUDIO_DIR"
    CMD='ffmpeg -hide_banner -v warning -i "$file" -ar 16000 -ac 1 "$DST_DIR/${name}.wav"'

    shopt -s nullglob
    file_list=("$SRC_DIR"/*.[mM][oO][vV])
    shopt -u nullglob  # 用完就關掉
    ;;
  transcribe)
    echo ":: 🙊 語音轉文字 (較久)"
    SRC_DIR="$AUDIO_DIR"
    DST_DIR="$TRANS_DIR"
    CMD='whisper "$file" --language Chinese --model medium --output_dir "$DST_DIR" --output_format srt'

    shopt -s nullglob
    file_list=("$SRC_DIR"/*.[wW][aA][vV])
    shopt -u nullglob
    ;;
  *)
    echo "用法: \"$0\" [extract|transcribe]"
    exit 1
    ;;
esac

mkdir -p "$DST_DIR" "$FINISH_DIR"

if [ ${#file_list[@]} -eq 0 ]; then
  echo ":: ❌ 找不到 .\"$EXT\" 檔案！"
  exit 1
fi

for file in "${file_list[@]}"; do
  filename=$(basename "$file")
  name="${filename%.*}"
  echo ":: ⏳ 處理中：\"$filename\""
  eval "$CMD"
  mv "$file" "$FINISH_DIR"
  echo ":: 🚚 處理完成。移動 \"$filename\" 到 \"$FINISH_DIR\""
done

echo ":: ✅ 轉譯檔案在 \"$DST_DIR\""
