import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import os
import logging
from pathlib import Path

from config import load_config, save_config
from sound_manager import SoundManager
from timer_settings import TimerSettingsWindow

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Timer")
        
        # 設定を読み込み
        self.config = load_config()
        
        # サウンドマネージャーを初期化
        self.sound_manager = SoundManager(self.config)
        
        # タイマーの状態を初期化
        self.timer_running = False
        self.work_seconds = self.config["timer"]["work_time"] * 60
        self.break_seconds = self.config["timer"]["break_time"] * 60
        self.current_timer = "work"
        
        # ログディレクトリを作成
        Path("log").mkdir(exist_ok=True)
        
        # CSVファイルの設定
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        self.csv_file = f"log/pomodoro_log_{self.start_date}.csv"
        self.ensure_csv_file()
        
        # ポモドーロカウントを初期化
        self.pomodoro_count = self.get_today_pomodoro_count()
        self.work_count = self.pomodoro_count + 1
        self.break_count = self.pomodoro_count + 1
        
        self.setup_ui()
        
    def setup_ui(self):
        """UIの初期化"""
        # タイマーのラベル
        self.timer_label = ttk.Label(
            self.master,
            text=f"{self.config['timer']['work_time']:02d}:00",
            font=("Arial", 24)
        )
        self.timer_label.pack(pady=10)
        
        # ポモドーロカウントフレーム
        count_frame = ttk.Frame(self.master)
        count_frame.pack(pady=5)
        
        # ポモドーロカウントのラベル
        self.pomodoro_label = ttk.Label(
            count_frame,
            text=f"{self.pomodoro_count}ﾎﾟﾓﾄﾞｰﾛ終了",
            font=("Arial", 14)
        )
        self.pomodoro_label.pack(side=tk.LEFT, padx=5)
        
        # カウント編集ボタン
        ttk.Button(
            count_frame,
            text="編集",
            command=self.edit_pomodoro_count,
            width=6
        ).pack(side=tk.LEFT)
        
        # カウントリセットボタン
        ttk.Button(
            count_frame,
            text="リセット",
            command=self.reset_pomodoro_count,
            width=6
        ).pack(side=tk.LEFT, padx=5)
        
        # メインボタンフレーム
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=5)
        
        # 開始/停止ボタン
        self.start_button = ttk.Button(
            button_frame,
            text="開始",
            command=self.toggle_timer
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # リセットボタン
        self.reset_button = ttk.Button(
            button_frame,
            text="リセット",
            command=self.reset_timer
        )
        self.reset_button.pack(side=tk.LEFT)
        
        # 設定フレーム
        settings_frame = ttk.Frame(self.master)
        settings_frame.pack(pady=5)
        
        # 最前面表示ボタン
        self.is_topmost = self.config["window"].get("topmost", True)
        self.topmost_button = ttk.Button(
            settings_frame,
            text="最前面：オン" if self.is_topmost else "最前面：オフ",
            command=self.toggle_topmost
        )
        self.topmost_button.pack(side=tk.LEFT, padx=5)
        
        # 音声モード切り替えボタン
        self.sound_mode_button = ttk.Button(
            settings_frame,
            text="音声：ビープ音" if self.config["sound"]["use_beep"] else "音声：WAV",
            command=self.toggle_sound_mode
        )
        self.sound_mode_button.pack(side=tk.LEFT, padx=5)
        
        # 設定ボタン
        self.settings_button = ttk.Button(
            settings_frame,
            text="設定",
            command=self.show_settings
        )
        self.settings_button.pack(side=tk.LEFT)
        
        # 音量スライダー
        volume_frame = ttk.LabelFrame(self.master, text="音量", padding="5")
        volume_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.volume = tk.IntVar(value=self.config["sound"]["volume"])
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume,
            command=self.on_volume_change
        )
        volume_scale.pack(fill=tk.X)
        
        # ウィンドウ設定を適用
        self.master.wm_attributes("-topmost", self.is_topmost)
        pos = self.config["window"]["position"]
        size = self.config["window"]["size"]
        self.master.geometry(f"{size['width']}x{size['height']}+{pos['x']}+{pos['y']}")
        
        # ウィンドウ位置の変更を監視
        self.master.bind("<Configure>", self.on_window_configure)
        
    def ensure_csv_file(self):
        """CSVファイルが存在しない場合、新規作成"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode="w", newline="", encoding="shift_jis") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "タイムスタンプ",
                    "開始時刻",
                    "リセット時刻",
                    "中断時刻",
                    "状態",
                    "カウント",
                ])
    
    def toggle_timer(self):
        """タイマーの開始/停止を切り替え"""
        if not self.timer_running:
            self.timer_running = True
            self.start_button.config(text="一時停止")
            self.sound_manager.play_start_sound()
            
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
            self.start_button.config(text="開始")
            
            # タイマー中断時刻を記録
            interruption_time = datetime.now()
            self.log_pomodoro(interruption_time=interruption_time)
    
    def reset_timer(self):
        """タイマーをリセット"""
        self.timer_running = False
        self.start_button.config(text="開始")
        self.current_timer = "work"
        self.work_seconds = self.config["timer"]["work_time"] * 60
        self.break_seconds = self.config["timer"]["break_time"] * 60
        
        # リセット時刻を記録
        reset_time = datetime.now()
        self.log_pomodoro(reset_time=reset_time)
        
        self.update_timer_label(self.work_seconds)
    
    def countdown(self, timer_seconds):
        """カウントダウンを実行"""
        if timer_seconds > 0 and self.timer_running:
            minutes, seconds = divmod(timer_seconds, 60)
            self.update_timer_label(minutes, seconds)
            
            if self.current_timer == "work":
                self.work_seconds = timer_seconds - 1
                # 離脱防止のための音を鳴らす
                total_work_seconds = self.config["timer"]["work_time"] * 60
                remaining_seconds = self.work_seconds % total_work_seconds
                interval = total_work_seconds // self.config["timer"]["reminder_interval"]
                
                if remaining_seconds in [interval * i for i in range(1, self.config["timer"]["reminder_interval"])]:
                    self.sound_manager.play_reminder_sound()
            else:
                self.break_seconds = timer_seconds - 1
                
            self.master.after(1000, self.countdown, timer_seconds - 1)
            
        elif timer_seconds == 0:
            self.sound_manager.play_start_sound()
            
            if self.current_timer == "work":
                self.current_timer = "break"
                self.break_seconds = self.config["timer"]["break_time"] * 60
                self.work_count += 1
                
                # ポモドーロのループ回数を増やす
                self.pomodoro_count += 1
                self.update_pomodoro_label()
                
                # タイマー開始時刻を記録
                self.start_time = datetime.now()
                self.log_pomodoro(start_time=self.start_time)
                
                self.countdown(self.break_seconds)
            else:
                self.current_timer = "work"
                self.work_seconds = self.config["timer"]["work_time"] * 60
                self.break_count += 1
                
                # タイマー開始時刻を記録
                self.start_time = datetime.now()
                self.log_pomodoro(start_time=self.start_time)
                
                self.countdown(self.work_seconds)
            
            # タイマーの文字色を更新
            self.update_timer_color()
    
    def update_timer_label(self, minutes, seconds=None):
        """タイマーのラベルを更新"""
        if seconds is None:
            seconds = minutes % 60
            minutes //= 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def update_timer_color(self):
        """タイマーの文字色を更新"""
        self.timer_label.config(
            foreground="black" if self.current_timer == "work" else "blue"
        )
    
    def update_pomodoro_label(self):
        """ポモドーロのループ回数のラベルを更新"""
        self.pomodoro_label.config(text=f"{self.pomodoro_count}ﾎﾟﾓﾄﾞｰﾛ終了")
        
    def edit_pomodoro_count(self):
        """ポモドーロカウントを編集"""
        dialog = tk.Toplevel(self.master)
        dialog.title("ポモドーロカウント編集")
        dialog.geometry("250x120")
        dialog.resizable(False, False)
        
        # メインフレーム
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # カウント入力
        count_frame = ttk.Frame(main_frame)
        count_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(count_frame, text="カウント:").pack(side=tk.LEFT)
        count_var = tk.StringVar(value=str(self.pomodoro_count))
        count_entry = ttk.Entry(count_frame, textvariable=count_var, width=10)
        count_entry.pack(side=tk.LEFT, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_count():
            try:
                new_count = int(count_var.get())
                if new_count < 0:
                    raise ValueError("カウントは0以上の値を入力してください")
                    
                self.pomodoro_count = new_count
                self.work_count = new_count + 1
                self.break_count = new_count + 1
                self.update_pomodoro_label()
                dialog.destroy()
                
            except ValueError as e:
                tk.messagebox.showerror("エラー", str(e))
        
        ttk.Button(
            button_frame,
            text="キャンセル",
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="保存",
            command=save_count
        ).pack(side=tk.RIGHT, padx=5)
        
        # モーダルウィンドウとして表示
        dialog.transient(self.master)
        dialog.grab_set()
        count_entry.focus()
        
    def reset_pomodoro_count(self):
        """ポモドーロカウントをリセット"""
        if tk.messagebox.askyesno("確認", "ポモドーロカウントをリセットしますか？"):
            self.pomodoro_count = 0
            self.work_count = 1
            self.break_count = 1
            self.update_pomodoro_label()
    
    def toggle_topmost(self):
        """最前面表示を切り替え"""
        self.is_topmost = not self.is_topmost
        self.master.wm_attributes("-topmost", self.is_topmost)
        self.topmost_button.config(
            text="最前面：オン" if self.is_topmost else "最前面：オフ"
        )
        # 設定を保存
        self.config["window"]["topmost"] = self.is_topmost
        save_config(self.config)
    
    def toggle_sound_mode(self):
        """音声モードを切り替え"""
        is_beep = self.sound_manager.toggle_sound_mode()
        self.sound_mode_button.config(
            text="音声：ビープ音" if is_beep else "音声：WAV"
        )
        # 設定を保存
        self.config["sound"]["use_beep"] = is_beep
        save_config(self.config)
    
    def on_volume_change(self, value):
        """音量が変更された時の処理"""
        volume = int(float(value))
        self.sound_manager.set_volume(volume)
        save_config(self.config)
    
    def show_settings(self):
        """設定ウィンドウを表示"""
        TimerSettingsWindow(self.master, self.config, self.apply_settings)
    
    def apply_settings(self, new_config):
        """新しい設定を適用"""
        self.config = new_config
        save_config(self.config)
        
        # タイマーをリセット
        self.reset_timer()
    
    def on_window_configure(self, event):
        """ウィンドウの位置が変更された時の処理"""
        if event.widget == self.master:
            # ウィンドウの現在の位置とサイズを取得
            geometry = event.widget.geometry()
            width, height, x, y = map(int, geometry.replace("+", "x").split("x"))
            
            # 設定を更新
            self.config["window"]["position"] = {"x": x, "y": y}
            self.config["window"]["size"] = {"width": width, "height": height}
            save_config(self.config)
    
    def log_pomodoro(self, start_time=None, reset_time=None, interruption_time=None):
        """ポモドーロの状態をログに記録"""
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
                self.pomodoro_count,
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
        
        try:
            with open(self.csv_file, mode="a", newline="", encoding="shift_jis") as file:
                writer = csv.writer(file)
                writer.writerow(row)
        except Exception as e:
            logger.error(f"ログの書き込みに失敗: {e}")
    
    def get_today_pomodoro_count(self):
        """当日のポモドーロ回数を取得"""
        today = datetime.now().strftime("%Y-%m-%d")
        pomodoro_count = 0
        
        try:
            with open(self.csv_file, mode="r", encoding="shift_jis") as file:
                reader = csv.reader(file)
                next(reader, None)  # ヘッダーをスキップ
                for row in reversed(list(reader)):
                    if row[0].startswith(today):
                        try:
                            count = int(row[5]) if len(row) > 5 and row[5].strip() else 0
                            pomodoro_count = max(pomodoro_count, count)
                        except ValueError:
                            logger.warning(f"無効なカウント値を検出: {row[5]}")
        except Exception as e:
            logger.error(f"ログの読み込みに失敗: {e}")
        
        return pomodoro_count

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
