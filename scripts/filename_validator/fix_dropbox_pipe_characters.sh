#!/bin/bash

# Script to replace pipe characters "|" with hyphens "-" in Dropbox Docs_Peter filenames
# Built by: AI Assistant (Claude)
# Date: 2025-11-05

echo "🔧 Fixing pipe characters in Dropbox Docs_Peter filenames..."
echo "============================================================"

# Change to the Dropbox Docs_Peter directory
cd "/Users/petermaxfield/Library/CloudStorage/Dropbox/Docs_Peter"

# Counter for tracking changes
count=0

# Find all files with pipe characters and process them
find . -name "*|*" -type f | while IFS= read -r file; do
    # Get the directory and filename
    dir=$(dirname "$file")
    filename=$(basename "$file")
    
    # Replace pipe characters with hyphens
    newfilename=$(echo "$filename" | sed 's/|/-/g')
    
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
echo "🎉 Completed! Processed files with pipe characters."
echo "📊 Run the validator again to verify the fixes."




