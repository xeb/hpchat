import os
import requests
from pathlib import Path
from openai import OpenAI
from hpchat import db

class TextToSpeech:
    def __init__(self, api_key):
        """
        Initialize the TextToSpeech class with an API key.
        """
        self.openai_api_key = os.environ.get("OPENAI_APIKEY_KEY")
        
        if not self.openai_api_key:
            with open(os.path.expanduser("~/.ssh/openai_api_key.txt"), "r") as f:
                self.openai_api_key = f.read().strip()

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable")
    

    def fetch_and_save_tts(self, text, output_dir, filename):
        """
        Fetch audio from OpenAI Text-to-Speech API and save it locally.

        Args:
            text (str): The text to be converted to speech.
            output_dir (str): The directory to save the audio file.
            filename (str): The name of the audio file.
        """
        try:
            print("Starting the TTS process...")
            print(f"API Key: {self.openai_api_key[:5]}*** (truncated for security)")
            print(f"Text: {text}")
            print(f"Output Directory: {output_dir}")
            print(f"Filename: {filename}")
            print(f"key: {self.openai_api_key}")

            client = OpenAI()

            # speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="echo",
                input=text
            )

            # Create output directory if it does not exist
            if not os.path.exists(output_dir):
                print(f"Output directory does not exist. Creating: {output_dir}")
                os.makedirs(output_dir)
            else:
                print(f"Output directory exists: {output_dir}")

            # Define the full file path
            file_path = os.path.join(output_dir, filename)
            print(f"File path set to: {file_path}")

            # Write the MP3 data to a file
            response.stream_to_file(file_path)
            print("Writing the MP3 file...")
            # with open(file_path, 'wb') as file:
            #     file.write(response["data"])

            print(f"File saved successfully to {file_path}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


# Usage example
def main(slug="faith-and-anxiety"):
    print("Starting main function...")

    # TODO Refactor this to pull the slut out of the args
    sermon = db.get(url_slug=slug)

    # TODO Mofidy th text so that its created during the pre-process step.
    
    text = "Join us for \"The Truth About Honesty,\" an enlightening sermon series designed to challenge your understanding of faith and transformation. Discover how salvation is not just about escaping punishment, but about healing, purpose, and real change. Through the inspiring story of Paul, learn that it's never too late to redirect your life, no matter your past. We'll also explore the anxieties that often hold us back and provide valuable insights to help you manage them effectively. If you're curious about faith or seeking a deeper connection, this series is for you. Tune in and find hope and inspiration for your journey!"
    #text = sermon["one_sentence_summary"]
    output_dir = "./tts_outputs"
    filename = f"{slug}.mp3"

    tts = TextToSpeech(api_key="")
    print("Invoking fetch_and_save_tts...")
    tts.fetch_and_save_tts(text, output_dir, filename)


if __name__ == "__main__":
    main()