#!/bin/bash

# ==============================================================================
# YERM: YouTube Comment Crawler - Execution Script
# ==============================================================================
#
# This script executes the youtube_crawler.py module to collect comments
# from a specified YouTube video.
#
# Usage:
#   ./run_crawler.sh
#
# Modify the variables in the "CONFIGURATION" section below to change the
# target URL, output files, and other crawler settings.

# --- CONFIGURATION ---

# Target YouTube video URL (Required)
# Please change this to the URL of the video you want to crawl.
VIDEO_URL="https://www.youtube.com/watch?v=M2WTUoy4y6E" # <-- IMPORTANT: Change this value

# Output directory for the CSV file
OUTPUT_DIR="data"
# Directory for the log file
LOG_DIR="logs"

# Output filename. A timestamp is used to make it unique.
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_CSV="${OUTPUT_DIR}/comments_${TIMESTAMP}.csv"
LOG_FILE="${LOG_DIR}/crawler_${TIMESTAMP}.log"

# --- SCRIPT EXECUTION ---

# Create directories if they do not exist.
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

echo "Starting YouTube Comment Crawler..."
echo "URL: $VIDEO_URL"
echo "Output CSV: $OUTPUT_CSV"
echo "Log File: $LOG_FILE"
echo "----------------------------------------"

# --- CRAWLER OPTIONS ---
# Uncomment one of the execution blocks below to use it.

# === Example 1: Full Crawl (for data collection) ===
# Crawls all comments, runs in headless mode, and saves to CSV and log files.
# The crawler will automatically stop scrolling when no new comments are loaded.
# You can add the --max-scroll <number> option to limit the number of scrolls.

python -m src.youtube_crawler \
    --url "$VIDEO_URL" \
    --output "$OUTPUT_CSV" \
    --log-file "$LOG_FILE" \
    --log-level INFO

# === Example 2: Test Crawl (for quick tests) ===
# Fetches only the first 20 loaded comments. Useful for checking if selectors are working correctly.
#
# python -m src.youtube_crawler \
#     --url "$VIDEO_URL" \
#     --use test --n 20 \
#     --headless \
#     --output "$OUTPUT_CSV" \
#     --log-file "$LOG_FILE" \
#     --log-level DEBUG

echo "----------------------------------------"
echo "Crawler task finished."
echo "Check the output file: $OUTPUT_CSV"
echo "For details, check the log file: $LOG_FILE"
