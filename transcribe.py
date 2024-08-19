import os
import tqdm
import whisper
from pathlib import Path

def transcribe_videos():
    video_dir = Path("videos")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    def get_model():
        return whisper.load_model("medium")

    pbar = tqdm.tqdm(list(video_dir.glob("*.mp4")))
    model = None
    for video_file in pbar:
        output_file = output_dir / f"{video_file.stem}.txt"
        pbar.set_description(f"Checking for {output_file}")
        
        if output_file.exists():
            print(f"Skipping {video_file.name}: Already transcribed")
            continue
        else:
            pbar.set_description(f"Transcribing {video_file.name}...")
            if not model:
                model = get_model()

            result = model.transcribe(str(video_file), language="English")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result["text"])
            
            print(f"Transcription complete for {video_file.name}")

    print("All transcriptions complete")

if __name__ == "__main__":
    transcribe_videos()
