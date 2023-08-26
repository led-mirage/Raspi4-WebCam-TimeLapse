# Raspberry Pi WebCam Time-Lapse

## Program Overview

This program captures and saves time-lapse videos using a webcam connected to a Raspberry Pi.

The webcam used is the Logicool C922n PRO.

## Features

- Press the tactile switch to start capturing, press again to stop.
- A green LED is on during startup.
- A red LED is on during capturing.
- Stop the program with Ctrl + C.

## Equipment

- Raspberry Pi 4 Model B 4GB
- Logicool C922n PRO HD Streaming Webcam
- Resistor-included LED
- Tactile switch
- Breadboard
- Several jumper wires

## Wiring

- GPIO 20 (Pin#38) -> LED anode (+) … Pilot lamp
- GPIO 26 (Pin#37) -> LED anode (+) … Shooting lamp
- GND (Pin#39) -> LED cathode (-)
- GPIO 21 (Pin#40) -> Tactile switch terminal 1
- 3.3V (Pin#17) -> Tactile switch terminal 2

## Device Image

![screenshot](https://github.com/led-mirage/Raspi4-WebCam-TimeLapse/assets/139528700/c3438c50-3738-4d17-8c78-59dc3bde44a3)

## Sample Video

https://github.com/led-mirage/Raspi4-WebCam-TimeLapse/assets/139528700/c538c1da-742f-4a9d-9cda-dc92b109d6ff

Resolution: 1920 x 1080, Interval: 5 seconds, Capture Time: 30 minutes, FPS: 30, Video Duration: 12 seconds

## Execution Environment

- Raspberry Pi 4 Model B 4GB
- Raspberry Pi OS 64bit Bullseye
- Python 3.11.4
- pigpio 1.78
- opencv-python 4.8.0.76

## Development Environment

- Visual Studio Code 1.76.0
- pyenv 2.3.24

## Source File Structure

- main.py … Main module
- timelapse.py … Time-lapse video capture class
- sample.py … Sample program

## Required Modules

You need the following modules to execute the program. Please install them in advance if they are not installed.

- pigpio
- opencv-python

You must start the pigpio daemon before running the program. Refer to [this link](https://github.com/led-mirage/Raspi4-LEDBlink-pigpio/blob/main/Readme.md) for instructions on installing and starting the pigpio daemon.

To install opencv-python, run:

```bash
pip install opencv-python
```

## Configuration

Edit the constants at the beginning of main.py as needed.

### GPIO

Modify the following constants to match your environment.

```py
PILOT_LED_PIN = 26  # GPIO number for pilot LED
VIDEO_LED_PIN = 20  # GPIO number for video LED
SWITCH_PIN = 21	    # GPIO number for tactile switch
```

### Time-Lapse Settings

Modify the following constants to suit your environment and the time-lapse video you want to create.

```py
CAPTURE_DEVICE = 0               # Camera device index. Typical USB webcam is 0.
CAPTURE_INTERVAL = 5             # Capture interval in seconds.
CAPTURE_DURATION = 120           # Total duration of the time-lapse capture in seconds.
CAPTURE_FPS = 24                 # Frame rate for the output video.
CAPTURE_FRAMESIZE = (1920, 1080) # Frame size for the output video.
OUTPUT_DIR = "output"            # Output directory for the time-lapse video.
OUTPUT_FILE = "timelapse.mp4"    # Output file name for the time-lapse video.
```

## Running the Program

### Clone

Open the Raspberry Pi terminal, navigate to the directory where you want to clone the program, and run the following command:

```bash
git clone https://github.com/led-mirage/Raspi4-WebCam-TimeLapse.git
```

### Execution

Run the following command to start the program:

```bash
python main.py
```

### Starting and Stopping Capture

When you press the tactile switch, the capture starts and the red LED lights up. Once the set time has elapsed or you press the tactile switch again, the video synthesis process begins. After the processing is complete, a time-lapse video is output.

If the resolution is 1920x1080, it takes approximately 1 minute and 45 seconds to synthesize a time-lapse video from 1000 captured frames. During the synthesis, the red LED will flash. Once the time-lapse video is output, the red LED will turn off.

### Program Termination

Press "Ctrl + C" in the terminal to stop the program.

## How to Automatically Run the Program When Raspberry Pi Starts

You can automatically run this program when Raspberry Pi starts by creating a custom systemd service. Here's how:

### Create a Service File

Create /etc/systemd/system/webcam-timelapse.service and save the following content:

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

Modify the following parts to match your environment:
- /usr/bin/python … Path to the Python executable
- /home/username/timelapse/ … Folder where the program is placed
- username … Your username

To create/edit the service file, you will need administrative privileges. Use a text editor with administrative privileges, as shown below:

```bash
sudo nano /etc/systemd/system/webcam-timelapse.service
```

### Reload the Service

After creating the service file,

 run the following command:

```bash
sudo systemctl daemon-reload
```

### Enable the Service

To automatically run the program at startup, enable the service by running:

```bash
sudo systemctl enable webcam-timelapse.service
```

### Start the Service

You can manually start the service by running:

```bash
sudo systemctl start webcam-timelapse.service
```

### Stopping the Service

If you want to stop the service, execute the following command:

```bash
sudo systemctl stop webcam-timelapse.service
```

### Disabling the Service

If you want to stop the service from automatically running, execute the following command:

```bash
sudo systemctl disable webcam-timelapse.service
```

## Reusing the Program

The `timelapse.py` (TimeLapse class) is independent, so I believe it can be used in other applications.

Here's a sample. This sample runs with only a Raspberry Pi and a webcam.

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

## Version History

### 1.0 (2023/08/24)
- First release

---
This document was translated into English by ChatGPT.
