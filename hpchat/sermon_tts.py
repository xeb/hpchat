import requests
import os

# Define a function to call OpenAI Text-to-Speech API and save the audio
# file in a local directory
def fetch_and_save_tts(api_key, text, output_dir, filename):
    try:
        print("Starting the TTS process...")
        print(f"API Key: {api_key[:5]}*** (truncated for security)")
        print(f"Text: {text}")
        print(f"Output Directory: {output_dir}")
        print(f"Filename: {filename}")

        # Define the API endpoint
        url = "https://api.openai.com/v1/text-to-speech"
        print(f"API Endpoint: {url}")

        # Prepare the HTTP POST request headers and payload
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }
        print("Headers and payload prepared.")

        # Make the HTTP POST request
        print("Sending request to the API...")
        response = requests.post(url, headers=headers, json=payload)

        # Check for successful response
        if response.status_code == 200:
            print("API request successful.")
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
            print("Writing the MP3 file...")
            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"File saved successfully to {file_path}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Usage example
# Replace `your_openai_api_key` with your actual API key
# Replace `Hello, this is a test!` with the desired text
def main():
    print("Starting main function...")
    api_key = "your_openai_api_key"
    text = "Hello, this is a test!"
    output_dir = "./tts_outputs"
    filename = "output.mp3"

    print("Invoking fetch_and_save_tts...")
    fetch_and_save_tts(api_key, text, output_dir, filename)

if __name__ == "__main__":
    main()
