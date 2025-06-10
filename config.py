import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# デフォルト設定
DEFAULT_CONFIG = {
    "window": {
        "position": {"x": 1920, "y": 875},
        "size": {"width": 300, "height": 150},
        "topmost": True,  # 最前面表示
    },
    "settings_window": {
        "position": {"x": 100, "y": 100},
        "size": {"width": 300, "height": 320},
    },
    "sound": {
        "volume": 50,  # 0-100
        "use_beep": True,
        "beep": {
            "frequency": 1000,  # Hz
            "duration": 200,    # ミリ秒
        }
    },
    "timer": {
        "work_time": 25,    # 分
        "break_time": 5,    # 分
        "reminder_interval": 3  # 作業時間中の通知回数
    }
}

CONFIG_FILE = "settings.json"


def ensure_config_file():
    """設定ファイルが存在しない場合、デフォルト設定で作成"""
    if not Path(CONFIG_FILE).exists():
        save_config(DEFAULT_CONFIG)


def load_config():
    """設定をJSONファイルから読み込む"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # デフォルト設定とマージして、新しい設定項目がある場合に対応
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"設定の読み込みに失敗: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """設定をJSONファイルに保存"""
    try:
        # 設定ファイルのディレクトリが存在することを確認
        config_path = Path(CONFIG_FILE)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # 一時ファイルに書き込んでから移動
        temp_file = f"{CONFIG_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        # 一時ファイルを本来のファイルに移動
        os.replace(temp_file, CONFIG_FILE)
        logger.info("設定を正常に保存しました")
        return True

    except IOError as e:
        logger.error(f"設定ファイルの書き込みに失敗: {e}")
        return False
    except json.JSONEncodeError as e:
        logger.error(f"設定のJSON変換に失敗: {e}")
        return False
    except Exception as e:
        logger.error(f"設定の保存中に予期せぬエラーが発生: {e}")
        return False
    finally:
        # 一時ファイルが残っている場合は削除
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"一時ファイルの削除に失敗: {e}")


# 初期化時に設定ファイルを確認
ensure_config_file()
