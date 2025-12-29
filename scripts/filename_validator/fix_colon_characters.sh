#!/bin/bash

# Script to replace colon characters ":" with underscores "_" in filenames
# Built by: AI Assistant (Claude)
# Date: 2025-11-05

echo "🔧 Fixing colon characters in filenames..."
echo "========================================"

# Change to the Files directory
cd "/Users/petermaxfield/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/Files"

# Counter for tracking changes
count=0

# Find all files with colon characters and process them
find . -name "*:*" -type f | while IFS= read -r file; do
    # Get the directory and filename
    dir=$(dirname "$file")
    filename=$(basename "$file")
    
    # Replace colon characters with underscores
    newfilename=$(echo "$filename" | sed 's/:/_/g')
    
    # Full paths
    oldpath="$file"
    newpath="$dir/$newfilename"
    
    echo "📄 Renaming:"
    echo "   FROM: $filename"
    echo "   TO:   $newfilename"
    echo ""
    
    # Perform the rename
    if mv "$oldpath" "$newpath"; then
        echo "✅ Success!"
        ((count++))
    else
        echo "❌ Failed to rename: $oldpath"
    fi
    echo "----------------------------------------"
done

echo ""
echo "🎉 Completed! Processed files with colon characters."
echo "📊 Run the validator again to verify the fixes."
