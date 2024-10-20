#!/bin/bash

# Check if youtube-dl is installed
if ! command -v yt-dlp &> /dev/null
then
    echo "yt-dlp is not installed. Please install it first."
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null
then
    echo "ffmpeg is not installed. Please install it first."
    exit 1
fi

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <YouTube URL> <start time> <duration>"
    exit 1
fi

URL=$1
START_TIME=$2
DURATION=$3

yt-dlp -f best --postprocessor-args "-ss $START_TIME -t $DURATION" -o "%(title)s-segment.%(ext)s" "$URL"

echo "Download complete, moving into videos directory..."
mkdir -p videos
mv *.mp4 videos/

