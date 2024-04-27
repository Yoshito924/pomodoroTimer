import tkinter as tk
from tkinter import ttk
import time
import winsound


class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Timer")

        self.timer_running = False
        self.work_seconds = 25 * 60  # 25分のタイマー
        self.break_seconds = 5 * 60  # 5分の休憩タイマー
        self.current_timer = "work"  # 現在のタイマーを追跡

        # タイマーのラベルを作成
        self.timer_label = ttk.Label(master, text="25:00", font=("Arial", 24))
        self.timer_label.pack(pady=20)

        # 開始/停止ボタンを作成
        self.start_button = ttk.Button(master, text="Start", command=self.toggle_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # リセットボタンを作成
        self.reset_button = ttk.Button(master, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side=tk.LEFT)

        # ウィンドウを常に最前面に表示
        master.wm_attributes("-topmost", True)

        # ウィンドウの初期表示位置を設定
        master.geometry("+{}+{}".format(1721, 876))

        # ウィンドウの位置が変更されたときのイベントを監視
        master.bind("<Configure>", self.on_window_configure)

    def on_window_configure(self, event):
        if event.widget == self.master:
            print("Window position: ({}, {})".format(event.x, event.y))

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_button.config(text="Stop")
            winsound.PlaySound(
                "pomodoroTimer/sounds/startBell.wav",  # スタート時の音を鳴らす（鳴らしたい音のファイルパスを書く）
                winsound.SND_FILENAME,
            )  # タイマー開始時に音を再生
            self.countdown()
        else:
            self.timer_running = False
            self.start_button.config(text="Start")

    def reset_timer(self):
        # タイマーをリセット
        self.timer_running = False
        self.start_button.config(text="Start")
        self.current_timer = "work"
        self.work_seconds = 25 * 60
        self.break_seconds = 5 * 60
        self.update_timer_label(self.work_seconds)

    def countdown(self):
        # 現在のタイマーが作業用か休憩用かを判断し、適切なタイマーを設定
        if self.current_timer == "work":
            timer_seconds = self.work_seconds
        else:
            timer_seconds = self.break_seconds

        # タイマーが動作中かつ残り時間が0より大きい場合、カウントダウンを続行
        if timer_seconds > 0 and self.timer_running:
            minutes, seconds = divmod(timer_seconds, 60)
            self.update_timer_label(minutes, seconds)
            if self.current_timer == "work":
                self.work_seconds -= 1
                # 8分と16分時点で音を鳴らす
                if self.work_seconds == 17 * 60 or self.work_seconds == 9 * 60:
                    winsound.PlaySound(
                        "pomodoroTimer/sounds/bubble.wav",
                        winsound.SND_FILENAME,  # 途中で集中が途切れていないか音を鳴らす（鳴らしたい音のファイルパスを書く）
                    )
            else:
                self.break_seconds -= 1
            self.master.after(1000, self.countdown)
        # タイマーが0になった場合、次のタイマー（作業用または休憩用）を開始
        elif timer_seconds == 0:
            if self.current_timer == "work":
                self.current_timer = "break"
                self.break_seconds = 5 * 60
            else:
                self.current_timer = "work"
                self.work_seconds = 25 * 60
            self.countdown()

    def update_timer_label(self, minutes, seconds=None):
        # タイマーのラベルを更新
        if seconds is None:
            seconds = minutes % 60
            minutes //= 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")


# メインウィンドウを作成
root = tk.Tk()
pomodoro_timer = PomodoroTimer(root)
root.mainloop()
