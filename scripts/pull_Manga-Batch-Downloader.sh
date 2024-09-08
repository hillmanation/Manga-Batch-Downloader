#!/bin/sh

# Path to repository
REPO_DIR="/root/manga-scripts/Manga-Batch-Downloader"

# Navigate to REPO_DIR
cd $REPO_DIR || { echo "Repository not found"; exit 1; }

# Fetch the latest changes from the repository
echo "Fetching changes from GitHub..."
git pull origin main || { echo "Git pull failed"; exit 1; }

# Install/Update Python dependencies
if [ -f "requirements.txt" ]; then
        echo "Installing/Updating Python dependencies..."
        pip3 install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }
fi