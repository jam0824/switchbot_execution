import pyaudio
import numpy as np
import time
import switchbot

# パラメータ設定
CHUNK = 1024               # 1回あたりのフレーム数
FORMAT = pyaudio.paInt16   # 音声フォーマット（16bit整数）
CHANNELS = 1               # モノラル
RATE = 44100               # サンプリングレート（Hz）
THRESHOLD = 600           # 音量の閾値（調整が必要な場合があります）
WAIT_TIME = 1000            # 次の実行までの待ち時間
next_exec_time = WAIT_TIME

# PyAudioオブジェクト生成
p = pyaudio.PyAudio()

# デフォルトの入力デバイス情報を取得して表示
default_device_info = p.get_default_input_device_info()
print("使用中のマイク:", default_device_info.get('name', '不明'))

# マイク入力ストリームをオープン（デフォルトのマイクが使用されます）
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("マイク入力を監視中...（Ctrl+Cで終了）")
try:
    while True:
        # マイクからデータ読み込み
        data = stream.read(CHUNK, exception_on_overflow=False)
        # numpy配列に変換
        audio_data = np.frombuffer(data, dtype=np.int16)
        # 平均絶対値を計算（単純な音量評価）
        amplitude = np.abs(audio_data).mean()
        # 閾値を超えたら「OK」と出力し、5秒待機
        print(amplitude)
        print(next_exec_time)
        if(next_exec_time > 0):
            next_exec_time -= 1
        if amplitude > THRESHOLD and next_exec_time == 0:
            print("**************************************************OK")
            bot = switchbot.SwitchBot()
            bot.exec_scene()
            next_exec_time = WAIT_TIME
except KeyboardInterrupt:
    print("終了します...")
finally:
    # ストリームとPyAudioを終了
    stream.stop_stream()
    stream.close()
    p.terminate()
