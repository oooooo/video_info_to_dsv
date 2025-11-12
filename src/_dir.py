import os
from dotenv import load_dotenv

load_dotenv(".env.setting")
load_dotenv()

VIDEO_DIR = os.getenv("VIDEO_DIR")
AUDIO_DIR = os.getenv("AUDIO_DIR")
TRANS_DIR = os.getenv("TRANS_DIR")
JSON_DIR = os.getenv("JSON_DIR")
DSV_DIR = os.getenv("DSV_DIR")
FINISH_DIR = os.getenv("FINISH_DIR")

for path in [VIDEO_DIR, AUDIO_DIR, TRANS_DIR, JSON_DIR, DSV_DIR, FINISH_DIR]:
    os.makedirs(path, exist_ok=True)
