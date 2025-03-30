import datetime
import os

class Logger:
    list_log = []
    file_name = ''
    log_max = 100
    log_count = 100

    def __init__(self, timing):
        self.log_max = timing
        self.log_count = timing
        
        # logsフォルダが存在しない場合は作成
        logs_folder = "logs"
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
        
        # 当日のファイル名を作成 (例: "logs/2025-03-31.log")
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.file_name = os.path.join(logs_folder, f"{current_date}.log")
        
        # 新しいログファイルを作成（既存の場合は上書き）
        open(self.file_name, 'w').close()

    def calc_amplitude_averate(self, list_amp):
        total = sum(list_amp)
        average = total / len(list_amp)
        return int(average)

    def add_log(self, data):
        log = ""
        self.list_log.append(data)
        # ログが一定量たまったら、平均値と最大値を計算してログに追記
        if len(self.list_log) >= self.log_max:
            average = self.calc_amplitude_averate(self.list_log)
            max_data = int(max(self.list_log))
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            log = f"{formatted_time},{average},{max_data}\n"
            self.append_string_to_file(log, self.file_name)
            self.list_log.clear()
        return log

    def append_string_to_file(self, text, file_name):
        """
        指定されたファイルに、指定された文字列を追記します。

        :param text: 追記する文字列
        :param file_name: 追記先のファイル名
        """
        with open(file_name, 'a') as f:
            f.write(text)
