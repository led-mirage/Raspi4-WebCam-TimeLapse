"""
Raspberry Pi WebCam Time-Lapse
Main module

Copylight (c) 2023 led-mirage
"""

import os
import pigpio
import signal
import time
from datetime import datetime
from timelapse import TimeLapse


PILOT_LED_PIN = 26  # GPIO number for pilot LED
VIDEO_LED_PIN = 20  # GPIO number for video LED
SWITCH_PIN = 21	    # GPIO number for tactile switch

CAPTURE_DEVICE = 0               # Camera device index. Typical USB webcam is 0.
CAPTURE_INTERVAL = 5             # Capture interval in seconds.
CAPTURE_DURATION = 120           # Total duration of the time-lapse capture in seconds.
CAPTURE_FPS = 24                 # Frame rate for the output video.
CAPTURE_FRAMESIZE = (1920, 1080) # Frame size for the output video.
OUTPUT_DIR = "output"            # Output directory for the time-lapse video.
OUTPUT_FILE = "timelapse.mp4"    # Output file name for the time-lapse video.
SERIAL_NUMBER_FILE = "serial_number.txt" # File name for saving serial numbers, used for sequential numbering per file.

pi = pigpio.pi()
pi.set_mode(PILOT_LED_PIN, pigpio.OUTPUT)
pi.set_mode(VIDEO_LED_PIN, pigpio.OUTPUT)
pi.set_mode(SWITCH_PIN, pigpio.INPUT)
pi.set_pull_up_down(SWITCH_PIN, pigpio.PUD_DOWN)


timelapse = TimeLapse(CAPTURE_DEVICE, CAPTURE_INTERVAL, CAPTURE_DURATION, CAPTURE_FPS, CAPTURE_FRAMESIZE)


def main():
    """
    Executes the main loop, monitoring the state of the tactile switch and LEDs.
    """
    print("Raspberry Pi WebCam Time-Lapse ver 1.0.0")

    timelapse.set_on_single_capture_callback(on_single_capture)
    timelapse.set_on_video_progress_callback(on_video_progress)
    timelapse.set_on_video_created_callback(on_video_created)

    set_led_status(PILOT_LED_PIN, True)

    while True:
        # Check if the tactile switch has been pressed
        if pi.read(SWITCH_PIN) == 1:
            if not timelapse.is_capturing:
                timelapse.start_capture(get_file_path())
                set_led_status(VIDEO_LED_PIN, True)
            else:
                timelapse.stop_capture()
            time.sleep(0.5)  # Debounce delay to handle switch chatter

        time.sleep(0.01)  # Sleep to reduce CPU usage


def get_file_path():
    """
    Generates a file path with a sequential number.

    Returns:
        str: The generated file path.
    """
    serial_number = get_next_serial_number()
    filename, extension = os.path.splitext(OUTPUT_FILE)
    numbered_filename = f"{filename}_{serial_number:04}{extension}"
    return os.path.join(OUTPUT_DIR, numbered_filename)


def get_next_serial_number():
    """
    Retrieves the next sequential number and writes it to the file.

    Returns:
        int: The next sequential number.
    """
    path = os.path.join(OUTPUT_DIR, SERIAL_NUMBER_FILE)
    if os.path.exists(path):
        with open(path, "r") as file:
            current_serial_number = int(file.readline().strip())
    else:
        current_serial_number = 0

    next_serial_number = current_serial_number + 1

    with open(path, "w") as file:
        file.write(str(next_serial_number))

    return next_serial_number


def set_led_status(pin, is_on):
    """
    Sets the status of the LED.

    Args:
        pin (int): The GPIO pin number controlling the LED.
        is_on (bool): True if the LED should be turned on, False if it should be turned off.

    """
    duty = 100 # 0-255
    if is_on:
        pi.set_PWM_dutycycle(pin, duty)
    else:
        pi.set_PWM_dutycycle(pin, 0)


def on_single_capture(file_path):
    """
    Handles the event when a single image is captured.

    Args:
        file_path (str): The file path of the captured image.
    """
    print(f"{file_path} is captured.")


def on_video_progress(processed_frames, total_frames):
    """
    Handles the event of video processing progress.

    Args:
        processed_frames (int): The number of frames that have been processed so far.
        total_frames (int): The total number of frames in the video.
    """
    if not hasattr(on_video_progress, "last_called"):
        on_video_progress.last_called = datetime.now()
    if not hasattr(on_video_progress, "led_on"):
        on_video_progress.led_on = False
        set_led_status(VIDEO_LED_PIN, on_video_progress.led_on)

    now = datetime.now()
    diff_time = now - on_video_progress.last_called
    if diff_time.total_seconds() >= 1:
        on_video_progress.led_on = not on_video_progress.led_on
        on_video_progress.last_called = now
        set_led_status(VIDEO_LED_PIN, on_video_progress.led_on)

    progress_percent = int((processed_frames / total_frames) * 100)
    print(f"\rVideo is {progress_percent}% processed.", end="")


def on_video_created(file_path):
    """
    Handles the event when the video is created after all captures.

    Args:
        file_path (str): The file path of the created video.
    """
    set_led_status(VIDEO_LED_PIN, False)
    print(f"\n{file_path} is created.")


def cleanup():
    """
    Performs cleanup actions when the program is terminated.
    """
    timelapse.stop_capture()
    set_led_status(PILOT_LED_PIN, False)
    set_led_status(VIDEO_LED_PIN, False)
    pi.stop()


def handle_exit(signum, frame):
    """Handles exit signals.

    Args:
        signum (int): Signal number.
        frame: Stack frame when the signal was sent.
    """
    cleanup()
    exit(0)


signal.signal(signal.SIGINT, handle_exit)   # Ctrl + C
signal.signal(signal.SIGHUP, handle_exit)   # Close Terminal
signal.signal(signal.SIGTERM, handle_exit)  # killed


try:
    main()
except Exception as e:
    print(e)
    pass
else:
    cleanup()
