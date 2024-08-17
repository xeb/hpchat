#!/bin/bash

# Directory containing the video files
video_dir="videos"

# Output directory for transcriptions
output_dir="output"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all mp4 files in the video directory
for video in "$video_dir"/*.mp4; do
    # Get the base name of the video file
    base_name=$(basename "$video")
    
    # Construct the expected output file name
    output_file="$output_dir/${base_name}.txt"
    
    # Check if the output file already exists
    if [ -f "$output_file" ]; then
        echo "Skipping $base_name: Already transcribed"
    else
        echo "Transcribing $base_name..."
        whisper "$video" --model=small --language=English --output_dir="$output_dir" --task transcribe
        echo "Transcription complete for $base_name"
    fi
done

echo "All transcriptions complete"