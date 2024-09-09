#!/bin/sh

SCRIPT_DIR="/root/manga-scripts"
DOWNLOADS="/sauce/manga_cbz"
LOG_FILE="/var/log/manga_downloader.log"
MANGA_FILE="assets/manga_list.txt"
TOR_PROXY="socks5://tor_proxy:9050"
MAX_CON=6

# Log the start time of the script
echo "[$(date)] Starting manga batch download process" >> $LOG_FILE

# Update the Manga Downloader repository
if $SCRIPT_DIR/Manga-Batch-Downloader/scripts/pull_Manga-Batch-Downloader.sh; then
        echo "[$(date)] Manga-Batch-Downloader repo updated" >> $LOG_FILE
fi

# Navigate to the batch downloader directory
cd $SCRIPT_DIR/Manga-Batch-Downloader || { echo "[$(date)] Failed to navigate to $SCRIPT_DIR/Manga-Batch-Downloader\nDoes this directory exist?" >> $LOG_FILE; exit 1; }

# Run the batch download script
if python3 manga-batch-downloader.py --export-dir $DOWNLOADS --manga-list $MANGA_FILE --max-containers $MAX_CON --torify-it $TOR_PROXY; then
        echo "[$(date)] Started the batch download tasks..." >> $LOG_FILE
else
        echo "[$(date)] Failed to start the manga batch download process..." >> $LOG_FILE
        exit 1
fi

# Log the end time of the script
echo "[$(date)] Manga batch download process completed" >> $LOG_FILE