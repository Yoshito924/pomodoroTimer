import tkinter as tk
from tkinter import ttk
import winsound


# 離脱防止サウンドを鳴らす間隔（作業タイマーワンサイクルの中で何回鳴らすか）
reminderInterval = 3
# 鳴らしたい音のファイルパスを書く↓
startSound = "pomodoroTimer/sounds/startBell.wav"  # スタート時の音
reminderSound = "pomodoroTimer/sounds/bubble.wav"  # 離脱防止の音


# -------------------------------------------------------------------------------------------------
oneMinutes = 1  # 1分は60秒
workTimerTime = 25  # 作業用タイマーは25分
breakTimerTime = 5  # 休憩用タイマーは5分


# -------------------------------------------------------------------------------------------------
class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Timer")

        self.timer_running = False
        self.work_seconds = workTimerTime * oneMinutes  # 25分のタイマー
        self.break_seconds = breakTimerTime * oneMinutes  # 5分の休憩タイマー
        self.current_timer = "work"  # 現在のタイマーを追跡
        self.pomodoro_count = 0  # 何回目のポモドーロか
        # タイマーのラベルを作成
        self.timer_label = ttk.Label(master, text="25:00", font=("Arial", 24))
        self.timer_label.pack(pady=10)

        # ポモドーロのループ回数のラベルを作成
        self.pomodoro_label = ttk.Label(master, text="0 ポモドーロ", font=("Arial", 14))
        self.pomodoro_label.pack(pady=5)

        # 開始/停止ボタンを作成
        self.start_button = ttk.Button(master, text="開始", command=self.toggle_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # リセットボタンを作成
        self.reset_button = ttk.Button(
            master, text="リセット", command=self.reset_timer
        )
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
            self.start_button.config(text="停止")
            winsound.PlaySound(
                startSound,  # スタート時の音を鳴らす
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
        self.work_seconds = workTimerTime * oneMinutes
        self.break_seconds = breakTimerTime * oneMinutes
        self.pomodoro_count = 0  # ポモドーロのループ回数をリセット
        self.update_timer_label(self.work_seconds)
        self.update_pomodoro_label()

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
                # 離脱防止のための音を鳴らす
                remainingSeconds = self.work_seconds % (oneMinutes * workTimerTime)
                if remainingSeconds in [
                    oneMinutes * workTimerTime // reminderInterval * i
                    for i in range(1, reminderInterval)
                ]:
                    winsound.PlaySound(
                        reminderSound,
                        winsound.SND_FILENAME,  # 途中で集中が途切れていないか音を鳴らす（鳴らしたい音のファイルパスを書く）
                    )
            else:
                self.break_seconds -= 1
            self.master.after(1000, self.countdown)
        # タイマーが0になった場合、次のタイマー（作業用または休憩用）を開始
        elif timer_seconds == 0:
            winsound.PlaySound(
                startSound,  # スタート時の音を鳴らす
                winsound.SND_FILENAME,
            )
            if self.current_timer == "work":
                self.current_timer = "break"
                self.break_seconds = breakTimerTime * oneMinutes
            else:
                self.current_timer = "work"
                self.work_seconds = workTimerTime * oneMinutes
                self.pomodoro_count += 1  # ポモドーロのループ回数を増やす
                self.update_pomodoro_label()
            self.countdown()

    def update_timer_label(self, minutes, seconds=None):
        # タイマーのラベルを更新
        if seconds is None:
            seconds = minutes % 60
            minutes //= 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def update_pomodoro_label(self):
        # ポモドーロのループ回数のラベルを更新
        self.pomodoro_label.config(text=f"{self.pomodoro_count} ポモドーロ")


# メインウィンドウを作成
root = tk.Tk()
pomodoro_timer = PomodoroTimer(root)
root.mainloop()
