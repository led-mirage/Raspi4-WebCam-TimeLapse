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
