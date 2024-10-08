import argparse
import subprocess
import sys
import docker
from src.mangadex_downloader import MangadexDownloader
from datetime import datetime

# Initialize client variable
client = None


def check_for_docker():
    # Check if Docker is installed and running/enabled
    global client  # Global variable to initialize Docker client for later image check
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


# noinspection PyUnresolvedReferences
def check_and_pull_images(image_names):
    for image_name in image_names:
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


# Check for required containers that we need to be running
def check_for_container(container):
    try:
        # Check to see if the torproxy image is running
        result = subprocess.run(["docker", "ps", "-a"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if container in result.stdout.decode():
            print(f"Confirmed container {container} running...")
            return True
        else:
            print(f"WARNING: Container {container} not running...")
            return False
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Unable to check for running container {container}: {str(e)}")
        return False


# noinspection PyUnresolvedReferences
def start_container(container, container_name, container_args=None):
    try:
        container_start = download_client = client.containers.run(
                container,  # Docker Image name
                detach=True,  # Run in detached mode
                name=container_name,  # Name of Container instance
                remove=True,  # Remove after container process stops
                network="tor" if container_name == "tor_proxy" else None,  # For when we're making tor_proxy
                ports={'9050/tcp': 9050} if container_name == "tor_proxy" else None,  # Same as above
                command=container_args
        )
        print(
            f"Started container '{container_name}' @ {datetime.now().strftime('%H:%M:%S')} with ID: "
            f"{container_start.id}")
        return container_name  # Return for tracking
    except docker.errors.APIError as e:
        print(f"Error starting container '{container_name}': {str(e)}")
        return None


def main():
    # Check if Docker is installed
    check_for_docker()

    # Gather a list of docker images we need to run the tool
    required_images = ["mansuf/mangadex-downloader"]  # , "dperson/torproxy"] <-- Not currently needed

    # Check for the image we need and pull it down if we don't have it
    check_and_pull_images(required_images)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Manga Downloader Script")
    parser.add_argument('--export-dir', type=str, required=True, help="Local directory to save downloaded manga to.")
    parser.add_argument('--manga-list', type=str, default='assets/manga-list.txt',
                        help="Path to manga list file, the default is included with this repository.")
    parser.add_argument('--max-containers', type=int, default=4,
                        help="Maximum number of simultaneous containers to spin up to run the batch downloads. Use "
                             "only as many containers as you're comfortable with. And probably less than the number "
                             "of cores your machine has.")
    parser.add_argument('--torify-it', type=str, help="(Currently Disabled) Anonymize the container over "
                                                      "TOR network to hide from those that would block our WAN IP.")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # If proxy is requested and torproxy is not running let's configure the tor network and start it
    if args.torify_it and not check_for_container("dperson/torproxy"):
        try:
            net_check = subprocess.run(["docker", "network", "ls"], check=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            if "tor" not in net_check.stdout.decode():  # Check for tor container network first
                print(f"Creating tor container network...")
                subprocess.run(["docker", "network", "create", "tor"], check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
                print(f"Tor container network created, starting torproxy on Tor network...")
                start_container("dperson/torproxy", "tor_proxy")
            else:
                print(f"Tor container network exists, starting torproxy on Tor network...")
                start_container("dperson/torproxy", "tor_proxy")
        except subprocess.CalledProcessError as e:
            print(f"Error: {str(e)} please manually create these before proceeding with tor proxy download settings...")
            sys.exit(0)

    # Create a MangaDownloader instance with the provided export directory
    downloader = MangadexDownloader(
        manga_list_file=args.manga_list,
        export_dir=args.export_dir,
        max_containers=args.max_containers,
        torify=args.torify_it,
        debug=args.debug
    )
    downloader.run()


if __name__ == "__main__":
    main()