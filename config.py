import pyaudio

# Audio settings
CHUNK = 1024               # 1回あたりのフレーム数
FORMAT = pyaudio.paInt16   # 音声フォーマット（16bit整数）
CHANNELS = 1               # モノラル
RATE = 44100               # サンプリングレート（Hz）

# Trigger settings
THRESHOLD = 300           # 音量の閾値（調整が必要な場合があります）
WAIT_TIME = 10000         # 次の実行までの待ち時間
LOG_TIMING = 100          # logをどれくらい貯めたら平均と最大を出すか
TERM_COUNT = 2            # term_triggerで、thresholdを何回超えたらtriggerするか

# File settings
OUTPUT_FILE_NAME = "output.csv"  # logの出力ファイル
WAV_FILE = "14000Hz_sine.wav"      # 再生するwavファイルの名前