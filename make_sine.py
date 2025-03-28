import numpy as np
import wave

# パラメータ設定
duration = 30.0          # 音の長さ（秒）
sample_rate = 48000     # サンプルレート（Hz）
frequency = 14000       # 正弦波の周波数（Hz）
amplitude = 32767       # 16ビットPCMの最大振幅

# 時間軸のデータ作成
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
# 15000Hzの正弦波の生成
data = (amplitude * np.sin(2 * np.pi * frequency * t)).astype(np.int16)

# WAVファイルの作成と書き込み
with wave.open("14000Hz_sine.wav", "w") as wf:
    wf.setnchannels(1)          # モノラル
    wf.setsampwidth(2)          # 16ビット（2バイト）
    wf.setframerate(sample_rate)
    wf.writeframes(data.tobytes())