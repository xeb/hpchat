import sys
import os
import yaml
import tqdm
from itertools import chain
from hpchat.runtime import Runtime
from hpchat.sermon import ParsedSermon
from hpchat import db

class Preprocessor():
    def __init__(self, runtime: Runtime = Runtime()):
        self.runtime = runtime
        db.create_sermons_table()
        pass
        
    def process_sermons(self):
        sermons = []
        for full_sermon_path in list(self.runtime.sermons_path.glob('*.txt')):
            with open(full_sermon_path, 'r') as f:
                print(f"Reading {full_sermon_path}")
                transcript = f.read()

                # Get the filename without the extension
                file_name = full_sermon_path.stem
                print(f"Checking {file_name}")
                existing_sermon = db.get(file_name)
                if existing_sermon:
                    print(f"Skipping! Already processed")
                    continue
                else:
                    print(f"Processing {file_name}")

                print("Parsing sermon content")
                parsed_sermon = self.runtime.parse_object(
                    prompt=f"The transcript is: <TRANSCRIPT>{transcript}</TRANSCRIPT>", 
                    system_prompt="Process this transcript into the specified sermon format, as best you can.",
                    format=ParsedSermon)
                
                # TODO: dynamically the keys from ParsedSermon to this dict
                sermon = {
                    "file_name": file_name,
                    "url_slug": parsed_sermon.url_slug,
                    "title": parsed_sermon.title,
                    "one_sentence_summary": parsed_sermon.one_sentence_summary,
                    "announcements": [a for a in parsed_sermon.announcements],
                    "biblical_references": [b for b in parsed_sermon.biblical_references],
                    "speaker_name": parsed_sermon.speaker_name,
                    "file_path": str(full_sermon_path),
                    "transcript": transcript
                }

                sermons.append(sermon)

                db.upsert(sermon)
        
        with open(self.runtime.sermon_list_path, 'w') as f:
            yaml.dump(sermons, f)


    def clean(self):
        for filename in os.listdir(self.runtime.sermons_path):
            file_path = os.path.join(self.runtime.sermons_path, filename)
            if os.path.isfile(file_path) and not filename.endswith('.txt') and not filename.endswith('.yaml'):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    def transcribe_videos(self):
        import whisper
        video_dir = self.runtime.media_path
        output_dir = self.runtime.sermons_path
        print(f"Transcribing videos from {video_dir} to {output_dir}")
        
        def get_model():
            return whisper.load_model("medium")
        
        pbar = tqdm.tqdm(list(chain(video_dir.glob("*.mp4"), video_dir.glob("*.mp3"))))
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
    print(preprocessor.runtime.sermons_path)
    # pass
    preprocessor.clean()
    # preprocessor.transcribe_videos()
    preprocessor.process_sermons()

