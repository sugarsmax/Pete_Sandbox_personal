#!/bin/bash

# Script to create a new Haldi JSON folder with current date
# Created on: 2025-09-28
# Pattern: Fusion_Haldi_JSON_YYYYMMDD

# Set the base directory
BASE_DIR="/Users/maxfiep/Documents/Haldi_JSON_Pete"

# Get current date in YYYYMMDD format
CURRENT_DATE=$(date "+%Y%m%d")

# Create folder name following the pattern
FOLDER_NAME="Fusion_Haldi_JSON_${CURRENT_DATE}"

# Full path for the new folder
FULL_PATH="${BASE_DIR}/${FOLDER_NAME}"

# Check if folder already exists
if [ -d "$FULL_PATH" ]; then
    echo "Folder already exists: $FULL_PATH"
    exit 1
fi

# Create the folder
mkdir -p "$FULL_PATH"

# Check if folder was created successfully
if [ $? -eq 0 ]; then
    echo "Successfully created folder: $FULL_PATH"
    echo "Folder name: $FOLDER_NAME"
    echo "Date: $CURRENT_DATE"
else
    echo "Failed to create folder: $FULL_PATH"
    exit 1
fi
