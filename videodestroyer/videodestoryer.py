import subprocess
import os
from tkinter import Tk, filedialog, messagebox
import random

def select_video_file():
    """Opens a file dialog to allow the user to select a video file."""
    root = Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(
        title="Select a video file to destroy",
        filetypes=(("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("All files", "*.*"))
    )
    return file_path

def destroy_video_quality(input_file, output_file):
    """
    Destroys a video's quality beyond recognition using extreme FFmpeg settings.
    This creates an intentionally unwatchable, heavily degraded output.
    """
    if not input_file:
        print("No file selected. Exiting.")
        return

    try:

        temp_file1 = "temp_destroyed_1.mp4"
        temp_file2 = "temp_destroyed_2.mp4"

        command1 = [
            'ffmpeg', '-y',  
            '-i', input_file,
            '-vf', 'scale=64:36,noise=alls=20:allf=t+u',  
            '-c:v', 'libx264',
            '-crf', '51',  
            '-preset', 'ultrafast',
            '-r', '5',  
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',  
            '-ar', '22050',  
            '-b:a', '16k',   
            '-ac', '1',     
            '-strict', '-2',  
            temp_file1
        ]

        print("Pass 1: Extreme downscaling and bit crushing...")
        subprocess.run(command1, check=True, capture_output=True)

        command2 = [
            'ffmpeg', '-y',
            '-i', temp_file1,
            '-vf', 'scale=32:18,scale=160:90:flags=neighbor,unsharp=5:5:-2.0:5:5:-2.0,eq=contrast=2:brightness=0.2',
            '-c:v', 'libx264',
            '-crf', '51',
            '-preset', 'ultrafast',
            '-maxrate', '50k',  
            '-bufsize', '25k',
            '-g', '1',  
            '-c:a', 'aac',
            '-ar', '22050',
            '-b:a', '12k',  
            '-ac', '1',
            '-strict', '-2',
            temp_file2
        ]

        print("Pass 2: Adding visual artifacts and distortions")
        subprocess.run(command2, check=True, capture_output=True)

        command3 = [
            'ffmpeg', '-y',
            '-i', temp_file2,
            '-vf', f'scale=80:45,scale=160:90:flags=neighbor,noise=alls=50:allf=t+u',
            '-c:v', 'libx264',
            '-crf', '51',
            '-preset', 'ultrafast',
            '-tune', 'fastdecode',
            '-profile:v', 'baseline',
            '-level', '3.0',
            '-maxrate', '32k',
            '-bufsize', '16k',
            '-r', '3',  
            '-g', '1',
            '-sc_threshold', '0',
            '-c:a', 'aac',
            '-ar', '22050',
            '-b:a', '12k',
            '-ac', '1',
            '-af', 'volume=0.5,lowpass=f=1000,highpass=f=300',  
            '-strict', '-2',
            output_file
        ]

        print("Pass 3: Final destruction with maximum artifacts...")
        subprocess.run(command3, check=True, capture_output=True)

        for temp_file in [temp_file1, temp_file2]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        print(f"\n🎉 Successfully Destroyed '{input_file}' into unwatchable '{output_file}'!")
        print("Video specs: 160x90 @ 3fps, ~32kbps video, 8kbps mono audio")
        print("Quality level: Potato")

        root = Tk()
        root.withdraw()
        messagebox.showinfo("Video Destroyed", 
                          f"Your video has been successfully destroyed\n\n"
                          f"Output: {output_file}\n"
                          f"Size reduction: Why\n"
                          f"Quality level: Unwatchable")

    except subprocess.CalledProcessError as e:
        print(f"Error during video destruction:\n{e.stderr.decode()}")
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please ensure it is installed and in your system's PATH.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def batch_destroy_videos():
    root = Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select video files to destroy (hold Ctrl for multiple)",
        filetypes=(("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("All files", "*.*"))
    )

    if file_paths:
        for i, input_file in enumerate(file_paths):
            filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"DESTROYED_{filename}.mp4"
            print(f"\n--- Destroying video {i+1}/{len(file_paths)}: {os.path.basename(input_file)} ---")
            destroy_video_quality(input_file, output_file)

if __name__ == "__main__":
    print("My video looks too good you say, this fixes that")
    print("=" * 50)
    print("This script will make your videos completely unwatchable")
    print("Choose your destruction method:")
    print("1. Destroy single video")
    print("2. Batch destroy multiple videos")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        input_video = select_video_file()
        if input_video:
            filename = os.path.splitext(os.path.basename(input_video))[0]
            output_video = f"DESTROYED_{filename}.mp4"
            destroy_video_quality(input_video, output_video)
    elif choice == "2":
        batch_destroy_videos()
    else:
        print("Invalid choice. Exiting.")
