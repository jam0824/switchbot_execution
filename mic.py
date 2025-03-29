import pyaudio
import numpy as np
import switchbot
import logger
import wave
import config  # config.pyからパラメーターを読み込み

class Mic:
    def __init__(
        self,
        audio_interface=None,
        logger_instance=None,
        bot_instance=None
    ):
        # config.pyからパラメーターをインポート
        self.chunk = config.CHUNK
        self.format = config.FORMAT
        self.channels = config.CHANNELS
        self.rate = config.RATE
        self.threshold = config.THRESHOLD
        self.wait_time = config.WAIT_TIME
        self.log_timing = config.LOG_TIMING
        self.term_count = config.TERM_COUNT
        self.output_file_name = config.OUTPUT_FILE_NAME
        self.wav_file = config.WAV_FILE

        # 依存性注入（引数で渡されたオブジェクトがなければデフォルトを生成）
        self.audio_interface = audio_interface if audio_interface is not None else pyaudio.PyAudio()
        self.logger = logger_instance if logger_instance is not None else logger.Logger(self.log_timing, self.output_file_name)
        self.bot = bot_instance if bot_instance is not None else switchbot.SwitchBot()

        # 入力ストリームの作成
        self.stream = self.audio_interface.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        default_device_info = self.audio_interface.get_default_input_device_info()
        print("使用中のマイク:", default_device_info.get('name', '不明'))

        # シングルトリガー用の状態変数
        self.single_next_exec_time = self.wait_time

        # タームトリガー用の状態変数
        self.term_next_exec_time = self.wait_time
        self.term_log = []
        self.over_threshold_log = []

    def read_audio_data(self):
        """マイクから読み込んだ生データをnumpy配列に変換して返す"""
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        return np.frombuffer(data, dtype=np.int16)

    def calculate_rms(self):
        """読み込んだデータからRMS値を計算する"""
        audio_data = self.read_audio_data()
        if audio_data.size == 0:
            return 0.0
        audio_data = audio_data.astype(np.float32)
        squared = np.square(audio_data)
        mean_squared = np.mean(squared)
        rms_value = np.sqrt(mean_squared)
        return 0.0 if np.isnan(rms_value) else rms_value

    def add_log(self, amplitude):
        """loggerに値を追加し、ログ文字列があれば出力する"""
        log_str = self.logger.add_log(amplitude)
        if log_str:
            print(log_str.rstrip('\n'))

    def terminate_stream(self):
        """ストリームとオーディオインターフェースを終了する"""
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()

    def play_wav(self, filename=None):
        """指定したWAVファイルを再生する（単発再生）"""
        if filename is None:
            filename = self.wav_file
        try:
            wf = wave.open(filename, 'rb')
        except FileNotFoundError:
            print(f"WAVファイル {filename} が見つかりません。")
            return

        output_stream = self.audio_interface.open(
            format=self.audio_interface.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        data = wf.readframes(self.chunk)
        while data:
            output_stream.write(data)
            data = wf.readframes(self.chunk)
        output_stream.stop_stream()
        output_stream.close()
        wf.close()

    # ----- シングルトリガー関連の処理 -----

    def process_single_trigger(self, amplitude):
        """
        1回分のシングルトリガーの処理を行う。
        - クールダウンタイムの更新
        - 閾値を超えてクールダウンが終了していればシーンを実行
        """
        if self.single_next_exec_time > 0:
            self.single_next_exec_time -= 1
            if self.single_next_exec_time == 0:
                print("READY")
        if amplitude > self.threshold and self.single_next_exec_time == 0:
            print("**************************************************OK")
            self.bot.exec_scene()
            self.single_next_exec_time = self.wait_time

    def single_trigger_loop(self):
        """無限ループでシングルトリガーの処理を実行する（Ctrl+Cで終了）"""
        try:
            while True:
                amplitude = self.calculate_rms()
                self.add_log(amplitude)
                self.process_single_trigger(amplitude)
        except KeyboardInterrupt:
            print("終了します...")
        finally:
            self.terminate_stream()

    # ----- タームトリガー関連の処理 -----

    def process_term_trigger(self, amplitude):
        """
        1回分のタームトリガーの処理を行う。
        - クールダウンタイムの更新
        - ログを蓄積し、一定数ごとに最大音量をチェック
        - 連続して閾値を超えた場合、シーンを実行
        """
        if self.term_next_exec_time > 0:
            self.term_next_exec_time -= 1
            if self.term_next_exec_time == 0:
                print("READY")
        self.term_log.append(amplitude)
        if len(self.term_log) >= self.log_timing:
            max_amp = int(max(self.term_log))
            if max_amp > self.threshold:
                self.over_threshold_log.append(max_amp)
            else:
                self.over_threshold_log.clear()
            if len(self.over_threshold_log) >= self.term_count and self.term_next_exec_time == 0:
                print("**************************************************OK")
                self.bot.exec_scene()
                self.term_next_exec_time = self.wait_time
            self.term_log.clear()

    def term_trigger_loop(self):
        """無限ループでタームトリガーの処理を実行する（Ctrl+Cで終了）"""
        try:
            while True:
                amplitude = self.calculate_rms()
                self.add_log(amplitude)
                self.process_term_trigger(amplitude)
        except KeyboardInterrupt:
            print("終了します...")
        finally:
            self.terminate_stream()
