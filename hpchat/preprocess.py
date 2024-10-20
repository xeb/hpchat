import os
import tqdm
from pathlib import Path
from hpchat.runtime import Runtime


class Preprocessor():
    def __init__(self, runtime: Runtime = Runtime()):
        self.root_path = runtime.root_path
        
        self.sermons_path = self.root_path / "sermons"
        Path(self.sermons_path).mkdir(exist_ok=True)
        
        self.video_path = self.root_path / "videos"
        Path(self.video_path).mkdir(exist_ok=True)

        self.sermon_list_path = self.sermons_path / "sermon_list.yaml"
        pass
        
    def clean(self):
        for filename in os.listdir(self.sermons_path):
            file_path = os.path.join(self.sermons_path, filename)
            if os.path.isfile(file_path) and not filename.endswith('.txt'):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    def transcribe_videos(self):
        import whisper
        video_dir = self.video_path
        output_dir = self.sermons_path
        print("Transcribing videos from {video_dir} to {output_dir}")
        
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
    preprocessor = Preprocessor()
    print(preprocessor.sermons_path)
    # pass
    preprocessor.clean()

    preprocessor.transcribe_videos()

