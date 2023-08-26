"""
Raspberry Pi WebCam Time-Lapse
Time-Lapse module

Copylight (c) 2023 led-mirage
"""

import cv2
import glob
import os
import time
import threading

class TimeLapse:
    """
    A class for creating time-lapse videos from a continuous video capture.

    Args:
        capture_device (int, optional): The device index for the camera. Defaults to 0.
        interval (int, optional): The interval in seconds between captures. Defaults to 1.
        duration (int, optional): The total duration in seconds for the time-lapse. Defaults to 60.
        fps (int, optional): Frames per second for the output video. Defaults to 24.
        frame_size (tuple of int, optional): The size of the frames in the video. Defaults to (1920, 1080).

    Methods:
        start_capture(output_path="output/timelapse.mp4"): Captures images and generates a time-lapse video.
    """


    def __init__(self, capture_device=0, interval=1, duration=60, fps=24, frame_size=(1920, 1080)):
        """
        Initializes the TimeLapse object with capture settings.

        Args:
            capture_device (int, optional): The device index for the camera. Defaults to 0.
            interval (int, optional): The interval in seconds between captures. Defaults to 1.
            duration (int, optional): The total duration in seconds for the time-lapse. Defaults to 60.
            fps (int, optional): Frames per second for the output video. Defaults to 24.
            frame_size (tuple of int, optional): The size of the frames in the video. Defaults to (1920, 1080).
        """
        self.capture_device = capture_device
        self.interval = interval
        self.duration = duration
        self.fps = fps
        self.frame_size = frame_size
        self._stop_signal = threading.Event()
        self.is_capturing = False
        self._capture_thread = None
        self._on_single_capture_callback = None
        self._on_video_progress_callback = None
        self._on_video_created_callback = None


    def start_capture(self, output_path="output/timelapse.mp4"):
        """
        Begins the timelapse capture process on a separate thread and returns immediately.
        
        Args:
            output_path (str, optional): Output path for the generated video file. Defaults to "output/timelapse.mp4".
        """
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self._capture_thread = threading.Thread(target=self._start_capture, args=(output_path,))
        self._stop_signal.clear()
        self._capture_thread.start()


    def stop_capture(self):
        """
        Stops the ongoing capture process and generates the time-lapse video.
        """
        if self._capture_thread:
            self._stop_signal.set()
            self._capture_thread.join()
            self._capture_thread = None


    def _start_capture(self, output_path="output/timelapse.mp4"):
        """
        Internal method to handle the capture process on a separate thread.

        Args:
            output_path (str, optional): Output path for the generated video file. Defaults to "output/timelapse.mp4".
        """
        self.output_path = output_path
        self.output_dir, self.output_file = os.path.split(output_path)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        self._delete_work_files()
        self._capture_images()
        self._generate_video()
        self.is_capturing = False


    def _capture_images(self):
        """
        Captures images at regular intervals and saves them as jpg files.
        """
        cap = cv2.VideoCapture(self.capture_device)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
        cap.set(cv2.CAP_PROP_AUTO_WB, 1.0)
        
        start_time = time.time()
        
        frame_count = 0
        while time.time() - start_time < self.duration and not self._stop_signal.is_set():
            time.sleep(self.interval)
            ret, frame = cap.read()
            if ret:
                frame_filename = os.path.join(self.output_dir, f"frame_{frame_count:06}.jpg")
                cv2.imwrite(frame_filename, frame)
                frame_count += 1
                if self._on_single_capture_callback:
                    self._on_single_capture_callback(frame_filename)
            else:
                print("Failed to capture frame.")
                return
        
        cap.release()
  

    def _generate_video(self):
        """
        Generates a video file from the captured images.
        """
        images = [img for img in os.listdir(self.output_dir) if img.endswith(".jpg")]
        images.sort()
        if len(images) == 0:
            return

        frame = cv2.imread(os.path.join(self.output_dir, images[0]))
        h, w, layers = frame.shape
        size = (w, h)

        out = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, size)

        for i in range(len(images)):
            img_path = os.path.join(self.output_dir, images[i])
            img = cv2.imread(img_path)
            out.write(img)
            if self._on_video_progress_callback:
                self._on_video_progress_callback(i + 1, len(images))

        out.release()

        if self._on_video_created_callback:
            self._on_video_created_callback(self.output_path)


    def _delete_work_files(self):
        """
        Deletes the temporary jpg files created during the capture process.
        """
        jpg_files = glob.glob(os.path.join(self.output_dir, '*.jpg'))
        for file in jpg_files:
            os.remove(file)


    def set_on_single_capture_callback(self, callback):
        """
        Sets the callback function to be called when a single image is captured.

        Args:
            callback (function): The function to be called when a single image is captured.
        """
        self._on_single_capture_callback = callback

    def set_on_video_progress_callback(self, callback):
        """
        Sets the callback function to be called when the video is processing.

        Args:
            callback (function): The function to be called during video processing.
        """
        self._on_video_progress_callback = callback


    def set_on_video_created_callback(self, callback):
        """
        Sets the callback function to be called when the video is created after all captures.

        Args:
            callback (function): The function to be called when the video is created.
        """
        self._on_video_created_callback = callback
