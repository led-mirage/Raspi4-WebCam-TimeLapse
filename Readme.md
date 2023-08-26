# Raspberry Pi WebCam Time-Lapse

## プログラム概要

ラズパイに接続したWebカメラでタイムラプス動画を撮影して保存するプログラムです。 

使用するWebカメラは Logicool C922n PRO です。

## 機能

- タクトスイッチを押すと撮影を開始し、もう一度押すと撮影を終了します
- 起動中はLED（緑）が点灯します
- 撮影中はLED（赤）が点灯します
- Ctrl + Cで停止します

## 機材

- Raspberry Pi 4 Model B 4GB
- Logicool C922n PRO HDストリーム ウェブカメラ
- 抵抗入りLED
- タクトスイッチ
- ブレッドボード
- ジャンプワイヤー数本

## 配線

- GPIO 20 (Pin#38) -> LEDアノード(+) … パイロットランプ
- GPIO 26 (Pin#37) -> LEDアノード(+) … 撮影ランプ
- GND (Pin#39) -> LEDカソード(-)
- GPIO 21 (Pin#40) -> タクトスイッチ端子１
- 3.3V (Pin#17) -> タクトスイッチ端子２

## 装置画像

![screenshot](https://github.com/led-mirage/Raspi4-WebCam-TimeLapse/assets/139528700/4b86e4ba-3b97-4b20-9951-ecbf89e5980f)

## サンプル動画

https://github.com/led-mirage/Raspi4-WebCam-TimeLapse/assets/139528700/34f8c1a1-4a4c-4b2d-8c03-2412367cead2

解像度：1920 x 1080　インターバル：5秒　撮影時間：30分　FPS：30　動画時間：12秒

## 実行環境

- Raspberry Pi 4 Model B 4GB
- Raspberry Pi OS 64bit Bullseye
- Python 3.11.4
- pigpio 1.78
- opencv-python 4.8.0.76

## 開発環境

- Visual Studio Code 1.76.0
- pyenv 2.3.24

## ソースファイル構成

- main.py … メインモジュール
- timelapse.py … タイムラプス動画撮影用クラス
- sample.py … サンプルプログラム

## 実行に必要なモジュール

実行には以下のモジュールが必要です。インストールされていない場合はあらかじめインストールしておいてください。

- pigpio
- opencv-python

プログラムを実行する前に pigpio のデーモンを起動しておく必要があります。pigpio のインストールとデーモンの起動については[ここ](https://github.com/led-mirage/Raspi4-LEDBlink-pigpio/blob/main/Readme.md)を参照してください。

opencv-python のインストールは次のようにします。

```bash
pip install opencv-python
```

## 設定

main.pyの先頭部分にある定数を必要に応じて書き換えてください。

### GPIO

利用している環境に合わせて以下の定数を書き換えます。

``` py
PILOT_LED_PIN = 26  # GPIO number for pilot LED
VIDEO_LED_PIN = 20  # GPIO number for video LED
SWITCH_PIN = 21	    # GPIO number for tactile switch
```

### タイムラプスの設定

利用している環境、作りたいタイムラプス動画に合わせて以下の定数を書き換えます。

``` py
CAPTURE_DEVICE = 0               # Camera device index. Typical USB webcam is 0.
CAPTURE_INTERVAL = 5             # Capture interval in seconds.
CAPTURE_DURATION = 120           # Total duration of the time-lapse capture in seconds.
CAPTURE_FPS = 24                 # Frame rate for the output video.
CAPTURE_FRAMESIZE = (1920, 1080) # Frame size for the output video.
OUTPUT_DIR = "output"            # Output directory for the time-lapse video.
OUTPUT_FILE = "timelapse.mp4"    # Output file name for the time-lapse video.
```

## プログラムの実行

### クローン

ラズパイのターミナルを開き、プログラムをクローンしたいディレクトリに移動し、次のコマンドを実行します。

```bash
git clone https://github.com/led-mirage/Raspi4-WebCam-TimeLapse.git
```

### 実行

以下のコマンドを実行するとプログラムが開始します。

```bash
python main.py
```

### キャプチャーの開始と停止

タクトスイッチを押すとキャプチャーが始まり、赤色LEDが点灯します。設定時間が経過するか、もう一度タクトスイッチを押すと動画の合成処理が開始され、処理が終わるとタイムラプス動画が出力されます。  

解像度が1920x1080の場合、1000フレームのキャプチャ画像からタイムラプス動画を合成するのに約1分45秒かかります。合成中は赤色LEDが点滅します。タイムラプス動画が出力されると赤色LEDが消灯します。

### プログラムの終了

ターミナルで「Ctrl + C」を押すとプログラムが停止します。

## ラズパイ起動時にプログラムを自動実行するには

独自のsystemdサービスを作成することで、このプログラムをラズパイが起動したときに自動実行させることができます。以下に手順を示します。

### サービスファイルの作成

/etc/systemd/system/webcam-timelapse.serviceを作成して、以下の内容を保存します。

```
[Unit]
Description=WebCam Time-Lapse

[Service]
ExecStart=/usr/bin/python /home/username/timelapse/main.py
WorkingDirectory=/home/username/timelapse/
Restart=always
User=username

[Install]
WantedBy=multi-user.target
```

ファイル中の以下の個所はご自身の環境に合わせて書き換えてください。
- /usr/bin/python … Pythonの実行ファイルへのパス
- /home/username/timelapse/ … プログラムを配置したフォルダ
- username … ご自身のユーザー名

サービスファイルを作成・変更するには管理者権限が必要です。下記例のように管理者権限でテキストエディタを起動し編集してください。

```bash
sudo nano /etc/systemd/system/webcam-timelapse.service
```

### サービスのリロード

サービスファイルを作成したら、systemdに新しいサービスファイルを認識させるために、次のコマンドを実行します。

```bash
sudo systemctl daemon-reload
```

### サービスの有効化

次のコマンドでサービスを自動起動するように設定します。

```bash
sudo systemctl enable webcam-timelapse.service
```

### サービスの実行

サービスをすぐに開始するには、以下のコマンドを実行します。

```bash
sudo systemctl start webcam-timelapse.service
```

### サービスの停止

もしサービスを停止したい場合は、以下のコマンドを実行します。

```bash
sudo systemctl stop webcam-timelapse.service
```

### サービスの無効化

もしサービスの自動実行をやめたい場合は、以下のコマンドを実行します。

```bash
sudo systemctl disable webcam-timelapse.service
```

## プログラムの再利用

timelapse.py (TimeLapse クラス)は独立しているので、別のアプリケーションでも使えると思います。

以下にサンプルを示します。このサンプルはラズパイとWebカメラのみで動作します。

```python
from timelapse import TimeLapse


def on_single_capture(file_path):
    print(f"{file_path} is captured.")

def on_video_progress(processed_frames, total_frames):
    progress_percent = int((processed_frames / total_frames) * 100)
    print(f"\rVideo is {progress_percent}% processed.", end="")

def on_video_created(file_path):
    print(f"\n{file_path} is created.")


timelapse = TimeLapse(
    interval = 1, duration=200, fps=20, frame_size=(1280, 720))

timelapse.set_on_single_capture_callback(on_single_capture)
timelapse.set_on_video_progress_callback(on_video_progress)
timelapse.set_on_video_created_callback(on_video_created)

timelapse.start_capture()
```

## バージョン履歴

### 1.0 (2023/08/26)
- ファーストリリース
