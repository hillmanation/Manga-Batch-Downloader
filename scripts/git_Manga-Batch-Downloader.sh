#!/bin/sh

# Path to repository
REPO_DIR="/root/manga-scripts/Manga-Batch-Downloader"
STAGING_FILE="/sauce/manga_staging_list.txt"
MANGA_LIST_FILE="$REPO_DIR/assets/manga_list.txt"
LOG_FILE="/var/log/manga_downloader.log"

# Function to remove the staging file
remove_staging_file() {
    if [ -f "$STAGING_FILE" ]; then
        rm "$STAGING_FILE" && echo "[$(date)] Removed $STAGING_FILE." >> "$LOG_FILE"
    else
        echo "[$(date)] $STAGING_FILE not found, nothing to remove." >> "$LOG_FILE"
    fi
}

# Navigate to REPO_DIR
cd $REPO_DIR || { echo "[$(date)] Repository not found" >> $LOG_FILE; exit 1; }

# Fetch the latest changes from the repository
echo "[$(date)] Fetching changes from GitHub..." >> $LOG_FILE
git pull origin main || { echo "[$(date)] Git pull failed" >> $LOG_FILE; exit 1; }

# Install/Update Python dependencies
if [ -f "requirements.txt" ]; then
        echo "[$(date)] Installing/Updating Python dependencies..." >> $LOG_FILE
        pip3 install -r requirements.txt || { echo "[$(date)] Failed to install dependencies" >> $LOG_FILE; exit 1; }
fi

# Check that the manga list file exists, in case something weird happened
if [ ! -f "$MANGA_LIST_FILE" ]; then
    echo "[$(date)] Manga list file not found, creating new file." >> $LOG_FILE
    touch "$MANGA_LIST_FILE"
fi
# Only run the repo update if the staging file exists
if [ -f "$STAGING_FILE" ]; then
  # Process the staging file and append new entries to manga_list.txt
  echo "[$(date)] Processing the staging list..." >> $LOG_FILE
  while IFS= read -r manga_url; do
      # Skip empty lines
      if [ -z "$manga_url" ]; then
          continue
      fi

      # Strip newlines and whitespace
      manga_url=$(printf "%s" "$manga_url" | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

      # Check if the manga_url already exists in manga_list.txt
      if ! grep -Fxq "$manga_url" "$MANGA_LIST_FILE"; then
          echo "[$(date)] Adding $manga_url to the manga list." >> $LOG_FILE
          echo "$manga_url" >> "$MANGA_LIST_FILE"
      else
          echo "[$(date)] $manga_url is already in the manga list, skipping." >> $LOG_FILE
      fi
  done < "$STAGING_FILE"

  # Commit and push changes to GitHub
  echo "[$(date)] Committing changes to GitHub..." >> $LOG_FILE
  git add "$MANGA_LIST_FILE"
  if git commit -m "Automated update: Added new entries to manga_list.txt from manga_staging_list.txt"; then
      echo "[$(date)] Commit successful, pushing changes to GitHub..." >> $LOG_FILE
      if git push origin main; then
          echo "[$(date)] Repository updated successfully." >> $LOG_FILE
          # Remove the staging file after successful repo update
          echo "[$(date)] Calling remove_staging_file..." >> "$LOG_FILE"
          remove_staging_file
      else
          echo "[$(date)] Git push failed after successful commit." >> $LOG_FILE
      fi
  else
      echo "[$(date)] Git commit failed, not pushing changes." >> $LOG_FILE
  fi
fi
