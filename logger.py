import datetime

class Logger:
    list_log = []
    file_name = ''
    log_max = 100
    log_count = 100

    def __init__(self, timing, file_name):
        self.log_max = timing
        self.log_count = timing
        self.file_name = file_name

    def calc_amplitude_averate(self, list_amp):
        total = sum(list_amp)
        average = total / len(list_amp)
        return int(average)

    def add_log(self, data):
        self.list_log.append(data)
        if len(self.list_log) >= self.log_max:
            average = self.calc_amplitude_averate(self.list_log)
            max_data = int(max(self.list_log))
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            log = str(formatted_time) + ',' + str(average) + ',' + str(max_data) + '\n'
            self.append_string_to_file(log, self.file_name)
            self.list_log.clear()


    def append_string_to_file(self, text, file_name):
        """
        指定されたファイルに、指定された文字列を追記します。

        :param text: 追記する文字列
        :param file_name: 追記先のファイル名
        """
        with open(file_name, 'a') as f:
            f.write(text)


    

    
