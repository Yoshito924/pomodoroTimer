import tkinter as tk
from tkinter import ttk, messagebox
import logging

from config import save_config

logger = logging.getLogger(__name__)


class TimerSettingsWindow:
    def __init__(self, parent, config, save_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("タイマー設定")
        # 設定ウィンドウのサイズと位置を復元
        settings_window_config = config.get("settings_window", {
            "position": {"x": 100, "y": 100},
            "size": {"width": 300, "height": 320}
        })
        pos = settings_window_config["position"]
        size = settings_window_config["size"]
        self.window.geometry(f"{size['width']}x{size['height']}+{pos['x']}+{pos['y']}")
        self.window.resizable(True, True)

        self.config = config
        self.save_callback = save_callback
        
        # ウィンドウ位置の変更を監視
        self.window.bind("<Configure>", self.on_window_configure)

        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 作業時間設定
        work_frame = ttk.LabelFrame(main_frame, text="作業時間", padding="5")
        work_frame.pack(fill=tk.X, pady=5)

        self.work_time = tk.StringVar(value=str(config["timer"]["work_time"]))
        ttk.Label(work_frame, text="分").pack(side=tk.RIGHT)
        ttk.Entry(work_frame, textvariable=self.work_time, width=10).pack(side=tk.RIGHT)

        # 休憩時間設定
        break_frame = ttk.LabelFrame(main_frame, text="休憩時間", padding="5")
        break_frame.pack(fill=tk.X, pady=5)

        self.break_time = tk.StringVar(value=str(config["timer"]["break_time"]))
        ttk.Label(break_frame, text="分").pack(side=tk.RIGHT)
        ttk.Entry(break_frame, textvariable=self.break_time, width=10).pack(side=tk.RIGHT)

        # 通知間隔設定
        reminder_frame = ttk.LabelFrame(main_frame, text="通知間隔", padding="5")
        reminder_frame.pack(fill=tk.X, pady=5)

        self.reminder_interval = tk.StringVar(value=str(config["timer"]["reminder_interval"]))
        ttk.Label(reminder_frame, text="回").pack(side=tk.RIGHT)
        ttk.Entry(reminder_frame, textvariable=self.reminder_interval, width=10).pack(side=tk.RIGHT)
        ttk.Label(reminder_frame, text="作業時間中に").pack(side=tk.LEFT)

        # 音量設定
        volume_frame = ttk.LabelFrame(main_frame, text="音量", padding="5")
        volume_frame.pack(fill=tk.X, pady=5)

        self.volume = tk.IntVar(value=config["sound"]["volume"])
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume
        )
        volume_scale.pack(fill=tk.X)

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.window.destroy
        ).pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="適用して閉じる",
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="適用",
            command=lambda: self.save_settings(close_window=False)
        ).pack(side=tk.RIGHT, padx=5)

        # モーダルウィンドウとして表示
        self.window.transient(parent)
        self.window.grab_set()

    def on_window_configure(self, event):
        """ウィンドウの位置とサイズが変更された時の処理"""
        if event.widget == self.window:
            # ウィンドウの現在の位置とサイズを取得
            geometry = event.widget.geometry()
            width, height, x, y = map(int, geometry.replace("+", "x").split("x"))
            
            # 設定を更新
            if "settings_window" not in self.config:
                self.config["settings_window"] = {}
            self.config["settings_window"]["position"] = {"x": x, "y": y}
            self.config["settings_window"]["size"] = {"width": width, "height": height}
            save_config(self.config)

    def save_settings(self, close_window=True):
        """設定を保存"""
        try:
            # 入力値を検証
            work_time = int(self.work_time.get())
            break_time = int(self.break_time.get())
            reminder_interval = int(self.reminder_interval.get())
            volume = self.volume.get()

            if work_time <= 0 or break_time <= 0 or reminder_interval <= 0:
                raise ValueError("値は正の整数を入力してください")

            # 設定を更新
            self.config["timer"]["work_time"] = work_time
            self.config["timer"]["break_time"] = break_time
            self.config["timer"]["reminder_interval"] = reminder_interval
            self.config["sound"]["volume"] = volume

            # コールバックを呼び出して設定を保存
            self.save_callback(self.config)

            # 設定を保存
            if close_window:
                self.window.destroy()

        except ValueError as e:
            logger.error(f"設定の保存に失敗: {e}")
            messagebox.showerror("エラー", str(e))
