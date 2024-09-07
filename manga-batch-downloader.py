import argparse
import subprocess
import sys
import docker
from src.mangadex_downloader import MangadexDownloader

# Initialize client variable
client = None


def check_for_docker():
    # Check if Docker is installed and running/enabled
    global client  # GLobal variable to intitialize Docker client for later image check
    try:
        # Check if docker is installed first
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Check if it is running
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Initialize a Docker client for image checking
        client = docker.from_env()
    except subprocess.CalledProcessError:
        print("Docker is either not installed or not running, exiting...")
        sys.exit(1)


def check_and_pull_image(image_name):
    # Check if the proper Docker image is available, and if not pull it
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        print(f"Docker image '{image_name}' not found locally. Pulling from Docker Hub...")
        try:
            # Pull from Docker Hub
            client.images.pull(image_name)
            print(f"Successfully pulled '{image_name}' from Docker Hub, moving on...")
        except docker.errors.APIerror as e:
            print(f"Error pulling image '{image_name}': {str(e)}")
            sys.exit(1)


def main():
    # Check if Docker is installed
    check_for_docker()

    # Check for the image we need and pull it down if we don't have it
    check_and_pull_image("mansuf/mangadex-downloader")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Manga Downloader Script")
    parser.add_argument('--export-dir', type=str, required=True, help="Local directory to save downloaded "
                                                                      "manga to.")
    parser.add_argument('--manga-list', type=str, default='assets/manga-list.txt',
                        help="Path to manga list file, the default is included with this repository.")
    parser.add_argument('--max-containers', type=int, default=4,
                        help="Maximum number of simultaneous containers to spin up to run the batch downloads. Use "
                             "only as many containers as you're comfortable with. And probably less than the number "
                             "of cores your machine has.")
    parser.add_argument('--torify-it', action='store_true',
                        help="Anonymize the container over TOR network to hide from those that would block our WAN IP.")
    args = parser.parse_args()

    # Create a MangaDownloader instance with the provided export directory
    downloader = MangadexDownloader(
        manga_list_file=args.manga_list,
        export_dir=args.export_dir,
        max_containers=args.max_containers,
        torify=args.torify_it
    )
    downloader.run()


if __name__ == "__main__":
    main()