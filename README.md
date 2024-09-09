# Manga Batch Downloader

Manga Batch Downloader is a Python script that automates the downloading of manga from a list of URLs using Docker containers. The script spins up multiple containers to download manga in parallel while allowing you to manage the number of concurrent downloads.  
`Currently only Mangadex url downloads are implemented`

## Features

- Uses Docker to spin up isolated containers for each manga download task.
- Supports batch downloading from a list of URLs.
- Automatically checks if Docker is installed, running, and whether the required Docker image is available.
- Ensures proper management of container instances, limiting the number of simultaneous downloads to a specified amount.

## Prerequisites

- **Docker**: Make sure the latest version of Docker is installed and running on your system.
- **Python 3.9**: The script is built using Python 3.9.

## Installation

### General Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/hillmanation/Manga-Batch-Downloader.git
   cd manga-batch-downloader
   ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure Docker is installed on your system. You can verify this running:
    ```bash
    docker --version
    docker info
    ```

4. Ensure the required Docker image (mansuf/mangadex-downloader) is available. The script will attempt to pull it from Docker Hub if it is not found.
Documentation on mansuf's awesome tool can be found here: https://github.com/mansuf/mangadex-downloader
    ```bash
    docker pull mansuf/mangadex-downloader
   ```

# Usage

The script accepts a list of manga URLs from a file and downloads the manga into a specified directory using multiple Docker containers.

# Command-line Arguments
- `--export-dir`: The local directory where the downloaded manga will be saved (required)  
- `--manga-list`: Path to a file containing a list of manga URLs (default: `assets/manga-list.txt`)  
- `--max-containers`: The maximum number of Docker containers to run at the same time (default: `4`)  
- ~~`--torify-it`: Run the containers through the TOR network using the Torsock wrapper (default: `false`)~~ >*Not currently implemented but leaving for future use*

## Example Usage
Run the below from the directory this repository is stored:
   ```bash
   python manga-batch-downloader.py --export-dir /path/to/manga/downloads --manga-list assets/manga-list.txt --max-containers 2
   ```

This command will download manga into `/path/to/manga/downloads` using a list of URLs provided in `assets/manga-list.txt` that comes packages with this repository, with up to 2 simultaneous downloads.

When you run the downloader you will see output similar to below:  
![image](https://github.com/user-attachments/assets/c214b109-1868-4db9-9332-0fcc08287ba6)

If you want to run the tool in the background you should be able to use `nohup` or `screen` to run the python process and still use your console. If you choose to do this you can check the running Docker containers with this command:  
```bash
docker ps -a
```
This will show you the currently running containers similar to below:  
![image](https://github.com/user-attachments/assets/b52b2bfc-ab66-4acd-b0ad-cb519e4019b6)

If you want to check the progress of a single container you can do so with the following command:
```bash
docker logs {container name} -f
# Example
docker logs horimiya -f
```
The `-f` flag will show you what the container is doing in real time, we used the container name `horimiya` which can be seen in the first entry in the above image on the right, use `ctrl+c` to leave this view.

## Manga List File Format

The manga list file should contain one URL per line. For example:
```
https://mangadex.org/title/7bf163e3-123a-41c1-b2bc-8254dbe5a09b/2-5-jigen-no-yuuwaku
https://mangadex.org/title/b7b09c13-cb6d-4a70-b8de-92bdf5a9dcab/tokyo-revengers
...
```

## How It Works
1. Docker Initialization: The script checks if Docker is installed and running on the system. If Docker is installed but not running, it attempts to start it.
2. Docker Image Check: It checks if the required Docker image (`mansuf/mangadex-downloader`) is available locally. If not, the script pulls it from Docker Hub.
3. ~~TOR and Torsocks (Optional): If the --torify-it flag is passed, the containers will run through the TOR network, anonymizing the download process.~~ >*Not currently implemented but leaving for future use*
4. Manga Download: The script reads a list of URLs from the specified manga list file and spawns multiple Docker containers to download manga, ensuring the number of concurrent downloads does not exceed the limit specified by `--max-containers`.

***

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests if you encounter any problems or have suggestions for improvements. I'll try to add more sites and sources in the future.
