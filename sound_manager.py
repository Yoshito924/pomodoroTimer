import logging
import math
from pathlib import Path

import winsound
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

logger = logging.getLogger(__name__)


class SoundManager:
    def __init__(self, config):
        self.config = config
        self.sound_enabled = True
        self.volume = config["sound"]["volume"]
        self.use_beep = config["sound"]["use_beep"]

        # 必要なディレクトリを作成
        Path("sounds").mkdir(exist_ok=True)

        # サウンドファイルのパス
        self.start_sound = "sounds/startBell.wav"
        self.reminder_sound = "sounds/bubble.wav"

        # Windowsのオーディオデバイスを取得
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            self.volume_interface = interface.QueryInterface(
                IAudioEndpointVolume
            )
            self.set_volume(self.volume)  # 初期音量を設定
        except Exception as e:
            logger.error(f"音量制御の初期化に失敗: {e}")
            self.volume_interface = None

    def play_start_sound(self):
        """開始/終了時の音を再生"""
        if not self.sound_enabled:
            return

        try:
            if self.use_beep:
                winsound.Beep(
                    self.config["sound"]["beep"]["frequency"],
                    self.config["sound"]["beep"]["duration"]
                )
            else:
                winsound.PlaySound(
                    self.start_sound,
                    winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        except Exception as e:
            logger.error(f"音声再生エラー: {e}")
            self.sound_enabled = False
            logger.warning("サウンドシステムを無効化しました")

    def play_reminder_sound(self):
        """リマインダー音を再生"""
        if not self.sound_enabled:
            return

        try:
            if self.use_beep:
                winsound.Beep(
                    self.config["sound"]["beep"]["frequency"],
                    self.config["sound"]["beep"]["duration"]
                )
            else:
                winsound.PlaySound(
                    self.reminder_sound,
                    winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        except Exception as e:
            logger.error(f"音声再生エラー: {e}")
            self.sound_enabled = False
            logger.warning("サウンドシステムを無効化しました")

    def toggle_sound_mode(self):
        """音声モードを切り替え（ビープ音 ⇔ WAV）"""
        self.use_beep = not self.use_beep
        self.config["sound"]["use_beep"] = self.use_beep
        return self.use_beep

    def set_volume(self, volume):
        """音量を設定（0-100）"""
        try:
            if self.volume_interface is not None:
                # 0-100の値を-65.25-0 dBに変換
                self.volume = max(0, min(100, volume))
                self.config["sound"]["volume"] = self.volume

                # 音量をデシベルに変換
                if self.volume == 0:
                    db = -65.25  # 最小値
                else:
                    db = math.log10(self.volume / 100.0) * 20.0
                    # -65.25 dB から 0 dB の範囲に制限
                    db = max(-65.25, min(0, db))

                self.volume_interface.SetMasterVolumeLevel(db, None)
                logger.info(f"音量を設定: {self.volume}% ({db:.2f} dB)")

        except Exception as e:
            logger.error(f"音量の設定に失敗: {e}")
