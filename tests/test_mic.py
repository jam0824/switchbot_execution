import pytest
import numpy as np
from unittest.mock import Mock, patch
from mic import Mic
import config

class TestMic:
    @pytest.fixture
    def mock_audio_interface(self):
        mock = Mock()
        mock.open.return_value = Mock()
        mock.get_default_input_device_info.return_value = {"name": "テストマイク"}
        return mock

    @pytest.fixture
    def mock_logger(self):
        return Mock()

    @pytest.fixture
    def mock_bot(self):
        return Mock()

    @pytest.fixture
    def mic(self, mock_audio_interface, mock_logger, mock_bot):
        return Mic(
            audio_interface=mock_audio_interface,
            logger_instance=mock_logger,
            bot_instance=mock_bot
        )

    def test_init(self, mic, mock_audio_interface):
        """初期化が正しく行われることを確認"""
        assert mic.audio_interface == mock_audio_interface
        assert mic.chunk == config.CHUNK
        assert mic.format == config.FORMAT
        mock_audio_interface.open.assert_called_once()

    def test_read_audio_data(self, mic):
        """音声データの読み込みが正しく行われることを確認"""
        # モックデータの準備
        mock_data = np.array([1, 2, 3], dtype=np.int16).tobytes()
        mic.stream.read.return_value = mock_data
        
        result = mic.read_audio_data()
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int16
        np.testing.assert_array_equal(result, np.array([1, 2, 3]))

    def test_calculate_rms(self, mic):
        """RMS値の計算が正しく行われることを確認"""
        # モックデータの準備
        test_data = np.array([1, 2, 3], dtype=np.int16)
        mock_data = test_data.tobytes()
        mic.stream.read.return_value = mock_data
        
        result = mic.calculate_rms()
        
        # float32に変換して計算
        expected_data = test_data.astype(np.float32)
        expected = np.sqrt(np.mean(np.square(expected_data)))
        
        assert result == pytest.approx(expected, rel=1e-5)

    def test_process_single_trigger_not_ready(self, mic):
        """クールダウン中はトリガーが発生しないことを確認"""
        mic.single_next_exec_time = 10
        mic.process_single_trigger(1000)  # 閾値を超える値
        
        assert mic.single_next_exec_time == 9
        mic.bot.exec_scene.assert_not_called()

    def test_process_single_trigger_ready(self, mic):
        """準備完了状態でトリガーが正しく発生することを確認"""
        mic.single_next_exec_time = 0
        mic.threshold = 100
        mic.process_single_trigger(150)  # 閾値を超える値
        
        assert mic.single_next_exec_time == mic.wait_time
        mic.bot.exec_scene.assert_called_once()

    def test_process_term_trigger(self, mic):
        """タームトリガーの処理が正しく行われることを確認"""
        mic.term_next_exec_time = 0
        mic.threshold = 100
        mic.term_count = 2
        mic.log_timing = 3
        
        # 閾値を超える値を連続で入力
        for _ in range(3):
            mic.process_term_trigger(150)
        
        assert len(mic.term_log) == 0  # ログがクリアされている
        assert len(mic.over_threshold_log) == 1  # 閾値超過ログが記録されている
        
        # さらに閾値を超える値を入力
        for _ in range(3):
            mic.process_term_trigger(150)
            
        mic.bot.exec_scene.assert_called_once()  # シーンが実行された

    def test_terminate_stream(self, mic):
        """ストリームが正しく終了されることを確認"""
        mic.terminate_stream()
        
        mic.stream.stop_stream.assert_called_once()
        mic.stream.close.assert_called_once()
        mic.audio_interface.terminate.assert_called_once()

    @patch('wave.open')
    def test_play_wav(self, mock_wave_open, mic):
        """WAVファイルの再生が正しく行われることを確認"""
        mock_wave = Mock()
        mock_wave_open.return_value = mock_wave
        mock_wave.readframes.side_effect = [b'data', b'']
        
        mic.play_wav("test.wav")
        
        mock_wave_open.assert_called_with("test.wav", 'rb')
        mock_wave.close.assert_called_once() 