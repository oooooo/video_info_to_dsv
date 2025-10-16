#!/bin/bash
# 整合流程主控腳本（可指定起始步驟）

set -e  # 若中途出錯即停止

START_STEP=${1:-1}  # ${變數名:-預設值} 名稱數字 1 指第一個命令列參數

echo "🚀 從 Step $START_STEP 開始..."

# step 1: 影片轉音訊
if [ "$START_STEP" -le 1 ]; then
    echo "▶ Step 1: 影片轉音訊"
    # sh src/s1_convert_audio.sh
    sh src/s_pipeline.sh extract
fi

# step 2: 語音轉文字
if [ "$START_STEP" -le 2 ]; then
    echo "▶ Step 2: 語音轉文字"
    # sh src/s2_transcribe_audio.sh
    sh src/s_pipeline.sh transcribe
fi

# step 3: AI 文字分析（Python）
if [ "$START_STEP" -le 3 ]; then
    echo "▶ Step 3: 文字分析"
    python3 src/s3_prompt.py
fi

# step 4: 寫入本地 CSV
if [ "$START_STEP" -le 4 ]; then
    echo "▶ Step 4: 寫入 CSV"
    python3 src/s4_to_csv.py
fi

echo "✅ 全部完成！"
