import pyaudio
import numpy as np
import switchbot
import logger

class Mic:
    # パラメータ設定
    CHUNK = 1024               # 1回あたりのフレーム数
    FORMAT = pyaudio.paInt16   # 音声フォーマット（16bit整数）
    CHANNELS = 1               # モノラル
    RATE = 44100               # サンプリングレート（Hz）
    THRESHOLD = 500           # 音量の閾値（調整が必要な場合があります）
    WAIT_TIME = 10000            # 次の実行までの待ち時間(1000=23秒)
    next_exec_time = WAIT_TIME
    LOG_TIMING = 100
    TERM_COUNT = 2
    OUTPUT_FILE_NAME = "output.csv"

    # PyAudioオブジェクト生成
    p = pyaudio.PyAudio()
    log = logger.Logger(LOG_TIMING, OUTPUT_FILE_NAME)
    bot = switchbot.SwitchBot()

    def __init__(self):
        self.stream = self.p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)
        # デフォルトの入力デバイス情報を取得して表示
        default_device_info = self.p.get_default_input_device_info()
        print("使用中のマイク:", default_device_info.get('name', '不明'))

    def get_amplitude(self):
        # マイクからデータ読み込み
        data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        # numpy配列に変換
        audio_data = np.frombuffer(data, dtype=np.int16)
        # 平均絶対値を計算（単純な音量評価）
        amplitude = np.abs(audio_data).mean()
        return amplitude
    
    def calculate_rms(self):
        # マイクからデータ読み込み
        data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        # numpy配列に変換
        audio_data = np.frombuffer(data, dtype=np.int16)
        # 空データなら 0 を返す
        if audio_data.size == 0:
            return 0.0

        # 計算前に float にキャストしておく
        audio_data = audio_data.astype(np.float32)
        squared = np.square(audio_data)          # 各サンプルを二乗
        mean_squared = np.mean(squared)           # 二乗した値の平均を計算
        rms_value = np.sqrt(mean_squared)         # 平均の平方根を取る

        # 万が一 NaN が出た場合は 0 を返す
        if np.isnan(rms_value):
            rms_value = 0.0

        return rms_value
    
    def add_log(self, amplitude):
        str_log = self.log.add_log(amplitude)
        if str_log != "":
            print(str_log.rstrip('\n'))

    def terminate_stream(self):
        # ストリームとPyAudioを終了
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


    def single_trigger(self):
        next_exec_time = self.WAIT_TIME
        try:
            while True:
                amplitude = self.calculate_rms()
                self.add_log(amplitude)
                
                if(next_exec_time > 0):
                    next_exec_time -= 1
                    if(next_exec_time == 0):
                        print("READY")

                if amplitude > self.THRESHOLD and next_exec_time == 0:
                    print("**************************************************OK")
                    self.bot.exec_scene()
                    next_exec_time = self.WAIT_TIME
        except KeyboardInterrupt:
            print("終了します...")
        finally:
            self.terminate_stream()

    def term_trigger(self):
        next_exec_time = self.WAIT_TIME
        list_term_log = []
        list_over_threshold = []
        try:
            while True:
                amplitude = self.calculate_rms()
                self.add_log(amplitude)

                if(next_exec_time > 0):
                    next_exec_time -= 1
                    if(next_exec_time == 0):
                        print("READY")

                list_term_log.append(amplitude)

                #listが一定数たまったら実行
                if len(list_term_log) >= self.LOG_TIMING:
                    max_amp = int(max(list_term_log))
                    # max_ampがthresholdを超えたらlist_over_thresholdにためる
                    if max_amp > self.THRESHOLD:
                        list_over_threshold.append(max_amp)
                    else:
                        #もし超えない場合があったらlist_over_thresholdをリセット
                        list_over_threshold.clear()
                    
                    #連続でmaxがthresholdを超えるかつReadyになっていたら実行
                    if len(list_over_threshold) >= self.TERM_COUNT and next_exec_time == 0:
                        print("**************************************************OK")
                        self.bot.exec_scene()
                        next_exec_time = self.WAIT_TIME
                    list_term_log.clear()

        except KeyboardInterrupt:
            print("終了します...")
        finally:
            self.terminate_stream()