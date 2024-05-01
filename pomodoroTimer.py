import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import winsound
import csv
from datetime import datetime
import os

# 離脱防止サウンドを鳴らす間隔（作業タイマーワンサイクルの中で何回鳴らすか）
reminderInterval = 3
# 鳴らしたい音のファイルパスを書く↓
startSoundPath = "pomodoroTimer/sounds/startBell.wav"  # スタート時の音
reminderSoundPath = "pomodoroTimer/sounds/bubble.wav"  # 離脱防止の音

# -------------------------------------------------------------------------------------------------
oneMinutes = 60  # 1分は60秒
workTimerTime = 25  # 作業用タイマーは25分
breakTimerTime = 5  # 休憩用タイマーは5分

# ウィンドウの初期表示位置の座標
windowPosition = (1908, 877)

# 起動時の日付を取得
start_date = datetime.now().strftime("%Y-%m-%d")
csv_file = f"pomodoroTimer/log/pomodoro_log_{start_date}.csv"

# CSVファイルが存在しない場合は新規作成し、ヘッダーを書き込む
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="shift_jis") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "タイムスタンプ",
                "開始時刻",
                "リセット時刻",
                "中断時刻",
                "状態",
                "カウント",
            ]
        )


# -------------------------------------------------------------------------------------------------
class PomodoroTimer:

    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Timer")

        self.timer_running = False
        self.work_seconds = workTimerTime * oneMinutes  # 25分のタイマー
        self.break_seconds = breakTimerTime * oneMinutes  # 5分の休憩タイマー
        self.current_timer = "work"  # 現在のタイマーを追跡

        # CSVファイルから今日の最新のポモドーロ回数を取得
        self.pomodoro_count = self.get_today_pomodoro_count()
        self.work_count = self.pomodoro_count + 1
        self.break_count = self.pomodoro_count + 1

        # タイマーのラベルを作成
        self.timer_label = ttk.Label(master, text="25:00", font=("Arial", 24))
        self.timer_label.pack(pady=10)

        # ポモドーロのループ回数のラベルを作成
        self.pomodoro_label = ttk.Label(
            master, text=f"{self.pomodoro_count}ﾎﾟﾓﾄﾞｰﾛ終了", font=("Arial", 14)
        )
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
        master.geometry("+{}+{}".format(windowPosition[0], windowPosition[1]))

        # ウィンドウの位置が変更されたときのイベントを監視
        master.bind("<Configure>", self.on_window_configure)

    def on_window_configure(self, event):
        if event.widget == self.master:
            print("Window position: ({}, {})".format(event.x, event.y))

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_button.config(text="一時停止")
            winsound.PlaySound(
                startSoundPath,  # スタート時の音を鳴らす
                winsound.SND_FILENAME,
            )

            # タイマー開始時刻を記録
            self.start_time = datetime.now()
            self.log_pomodoro(start_time=self.start_time)

            self.countdown(
                self.work_seconds
                if self.current_timer == "work"
                else self.break_seconds
            )
        else:
            self.timer_running = False
            self.start_button.config(text="Start")

            # タイマー中断時刻を記録
            interruption_time = datetime.now()
            self.log_pomodoro(interruption_time=interruption_time)

    def reset_timer(self):
        # タイマーをリセット
        self.timer_running = False
        self.start_button.config(text="開始")
        self.current_timer = "work"
        self.work_seconds = workTimerTime * oneMinutes
        self.break_seconds = breakTimerTime * oneMinutes

        # リセット時刻を記録
        reset_time = datetime.now()
        self.log_pomodoro(reset_time=reset_time)

        self.update_timer_label(self.work_seconds)

    def countdown(self, timer_seconds):
        if timer_seconds > 0 and self.timer_running:
            minutes, seconds = divmod(timer_seconds, 60)
            self.update_timer_label(minutes, seconds)
            if self.current_timer == "work":
                self.work_seconds = timer_seconds - 1
                # 離脱防止のための音を鳴らす
                remainingSeconds = self.work_seconds % (oneMinutes * workTimerTime)
                if remainingSeconds in [
                    oneMinutes * workTimerTime // reminderInterval * i
                    for i in range(1, reminderInterval)
                ]:
                    winsound.PlaySound(
                        reminderSoundPath,
                        winsound.SND_FILENAME,  # 途中で集中が途切れていないか音を鳴らす（鳴らしたい音のファイルパスを書く）
                    )
            else:
                self.break_seconds = timer_seconds - 1
            self.master.after(1000, self.countdown, timer_seconds - 1)
        elif timer_seconds == 0:
            winsound.PlaySound(
                startSoundPath,  # スタート時の音を鳴らす
                winsound.SND_FILENAME,
            )
            if self.current_timer == "work":
                self.current_timer = "break"
                self.break_seconds = breakTimerTime * oneMinutes
                self.work_count += 1  # カウントを増やす位置を変更

                # ポモドーロのループ回数を増やす
                self.pomodoro_count += 1
                self.update_pomodoro_label()

                # タイマー開始時刻を記録
                self.start_time = datetime.now()
                self.log_pomodoro(start_time=self.start_time)

                self.countdown(self.break_seconds)
            else:
                self.current_timer = "work"
                self.work_seconds = workTimerTime * oneMinutes
                self.break_count += 1  # カウントを増やす位置を変更

                # タイマー開始時刻を記録
                self.start_time = datetime.now()
                self.log_pomodoro(start_time=self.start_time)

                self.countdown(self.work_seconds)

            # タイマーの文字色を更新
            self.update_timer_color()

    def log_pomodoro(self, start_time=None, reset_time=None, interruption_time=None):
        row = []

        if start_time:
            # タイマー開始時の記録
            timer_type = "work" if self.current_timer == "work" else "break"
            count = (
                self.work_count if self.current_timer == "work" else self.break_count
            )
            row = [
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                start_time.strftime("%H:%M:%S"),
                "",
                "",
                timer_type,
                count,
            ]
        elif reset_time:
            # リセットボタン押下時の記録
            row = [
                reset_time.strftime("%Y-%m-%d %H:%M:%S"),
                "",
                reset_time.strftime("%H:%M:%S"),
                "",
                "",
                self.pomodoro_count,  # リセット時のポモドーロのカウントを記録
            ]
        else:
            # ポモドーロ中断時の記録
            timer_type = "work" if self.current_timer == "work" else "break"
            count = (
                self.work_count if self.current_timer == "work" else self.break_count
            )
            row = [
                interruption_time.strftime("%Y-%m-%d %H:%M:%S"),
                "",
                "",
                interruption_time.strftime("%H:%M:%S"),
                timer_type,
                count,
            ]

        with open(csv_file, mode="a", newline="", encoding="shift_jis") as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def update_timer_label(self, minutes, seconds=None):
        # タイマーのラベルを更新
        if seconds is None:
            seconds = minutes % 60
            minutes //= 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def update_timer_color(self):
        # タイマーの文字色を更新
        if self.current_timer == "work":
            self.timer_label.config(foreground="black")
        else:
            self.timer_label.config(foreground="blue")

    def update_pomodoro_label(self):
        # ポモドーロのループ回数のラベルを更新
        self.pomodoro_label.config(text=f"{self.pomodoro_count}ﾎﾟﾓﾄﾞｰﾛ終了")

    def get_today_pomodoro_count(self):
        # 当日の日付を取得
        today = datetime.now().strftime("%Y-%m-%d")

        # 当日のポモドーロ回数を取得
        pomodoro_count = 0
        with open(csv_file, mode="r", encoding="shift_jis") as file:
            reader = csv.reader(file)
            next(reader, None)  # ヘッダーをスキップ
            for row in reversed(list(reader)):
                if row[0].startswith(today):
                    try:
                        count = int(row[5]) if len(row) > 5 and row[5].strip() else 0
                        pomodoro_count = max(pomodoro_count, count)
                    except ValueError:
                        pass

        return pomodoro_count


# メインウィンドウを作成
root = tk.Tk()
pomodoro_timer = PomodoroTimer(root)
root.mainloop()
