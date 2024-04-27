
# ループするポモドーロタイマー

このアプリケーションは、25分と5分のタイマーを繰り返すポモドーロタイマーのデスクトップアプリです。
自分用に作りましたが、よければ使ってください。

## 特徴

- 25分と5分のタイマーを自動的に切り替えます。
- 元々自分が使う用なので広告はなどは表示されません。
- 一度タイマーを起動したら、ずっとつけっぱなしでポモドーロを何周もできます。
- 作業時間の25分間の中、残り17分と9分あたりでも音が鳴るので、一集中力が途切れて別のことをやりかけても最小限で帰って来れる公算が大きいです笑

## インストールと実行

1. このリポジトリをクローンします。
2. Python 3.x がインストールされていることを確認します。
3. `pomodoroTimer.py` ファイルを実行します。

## カスタマイズ

サウンドを変更したい場合は、`sounds` ディレクトリの中に鳴らしたいサウンドファイルを入れて、`pomodoroTimer.py` の以下の行を書き換えてください。

- 開始音：`winsound.PlaySound("pomodoroTimer\\sounds\\startBell.wav", winsound.SND_FILENAME)`
- リマインダー音：`winsound.PlaySound("pomodoroTimer\\sounds\\reminder.wav", winsound.SND_FILENAME)`

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

## 連絡先

質問やフィードバックがある場合は、下記のGoogleフォームからどうぞ
https://docs.google.com/forms/d/1lAoN_y9oH1Q2u9OWjHJ6Dv0cpD750wGKOyaD0HyNC3g/edit
