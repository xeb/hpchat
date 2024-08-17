import os
import whisper
from pathlib import Path

def transcribe_videos():
    # Directory containing the video files
    video_dir = Path("videos")

    # Output directory for transcriptions
    output_dir = Path("output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Load the Whisper model
    model = whisper.load_model("small")

    # Loop through all mp4 files in the video directory
    for video_file in video_dir.glob("*.mp4"):
        # Construct the expected output file name
        output_file = output_dir / f"{video_file.stem}.txt"
        
        # Check if the output file already exists
        if output_file.exists():
            print(f"Skipping {video_file.name}: Already transcribed")
        else:
            print(f"Transcribing {video_file.name}...")
            
            # Transcribe the video
            result = model.transcribe(str(video_file), language="English")
            
            # Write the transcription to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result["text"])
            
            print(f"Transcription complete for {video_file.name}")

    print("All transcriptions complete")

if __name__ == "__main__":
    transcribe_videos()