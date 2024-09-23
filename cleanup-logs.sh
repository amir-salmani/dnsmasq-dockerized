#!/bin/sh
# cleanup-logs.sh

# Set the maximum age of log files in days
MAX_AGE=7

# Set the maximum size of the log directory in MB
MAX_SIZE=10000

# Clean up old log files
find /logs -type f -mtime +$MAX_AGE -delete

# If the directory is still too large, remove the oldest files
while [ $(du -sm /logs | cut -f1) -gt $MAX_SIZE ]; do
    oldest_file=$(find /logs -type f -printf '%T+ %p\n' | sort | head -n 1 | cut -d' ' -f2-)
    rm "$oldest_file"
done

# Truncate large log files
find /logs -type f -size +10M | while read file; do
    tail -n 1000 "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done