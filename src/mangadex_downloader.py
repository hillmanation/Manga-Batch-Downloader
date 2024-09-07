import docker
import subprocess
import time
import re
from datetime import datetime


def valid_container_name(url):
    # # Get just the last part of the url for the instance name
    container_name = url.rsplit('/', 1)[-1]

    # Oshi no Ko is weird, so it's url path ending started with a '-' which is bad juju
    # so just in case let's filter for that here and ensure we start with an alphanumeric
    if not re.match(r'^[a-zA-Z0-9]', container_name):  # Check if the string starts with a non-alphanumeric
        # I could do some logic here and waste a lot of time, or we can just prepend something for the same effect
        container_name = 'something' + container_name
    return container_name


class MangadexDownloader:
    def __init__(self, manga_list_file, export_dir, max_containers, torify):
        # Initialize Docker client
        self.client = docker.from_env()
        self.manga_list_file = manga_list_file
        self.volume_mapping = export_dir
        self.max_containers = max_containers
        self.torify_it = torify  # option to enable running the containers over torsocks
        self.running_containers = []
        self.defaults = "--no-group-name --use-chapter-title --delay-requests 1.5 --save-as 'cbz'"

    # Start download container instance
    def start_download(self, instance_name, command_args):
        if self.torify_it:  # If torify is requested we have to start the container with subprocess
            docker_command = [  # Build the command line arguments
                "torsocks", "docker", "run",  # Run docker with the torsocks wrapper
                "--detach",
                "--name", instance_name,
                "--volume", f"{self.volume_mapping}:/downloads:rw",
                "--rm",
                "mansuf/mangadex-downloader"
            ] + command_args.split()  # Append the url and default arguments from {self.defaults}

            try:  # Call subprocess to start the torified container
                print(f"Torify it: {' '.join(docker_command)}")
                result = subprocess.run(' '.join(docker_command), check=True, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                print(
                    f"Started container '{instance_name}' with torsocks: {self.torify_it} @ "
                    f"{datetime.now().strftime('%H:%M:%S')} with ID: {result.stdout.decode()}")
                return instance_name
            except subprocess.CalledProcessError as e:
                print(f"Error starting container '{instance_name}' with torsocks: {e.stderr.decode()}")
                return None
        else:
            # Start a Docker container for downloading manga from a url without torify using python module method
            try:
                download_client = self.client.containers.run(
                    "mansuf/mangadex-downloader",  # Docker Image name
                    detach=True,  # Run in detached mode
                    name=instance_name,  # Name of Container instance
                    volumes={self.volume_mapping: {"bind": "/downloads", "mode": "rw"}},  # Local volume mapping
                    remove=True,  # Remove after container process stops
                    command=command_args
                )
                print(
                    f"Started container '{instance_name}' @ {datetime.now().strftime('%H:%M:%S')} with ID: "
                    f"{download_client.id}")
                return instance_name  # Return for tracking
            except docker.errors.APIError as e:
                print(f"Error starting container '{instance_name}': {str(e)}")
                return None

    # Read in list of manga from a file
    def read_manga_list(self):
        manga_urls = []
        try:
            with open(self.manga_list_file, 'r') as f:
                for line in f:
                    # Strip any whitespace and append the url
                    manga_urls.append(line.strip())
        except FileNotFoundError:
            print(f"Error: File '{self.manga_list_file}' not found.")
        return manga_urls

    def manage_containers(self):
        # We're limiting the number of processes (containers) so we'll check to see how many containers are running
        # here and only continue to the next url if the number of running containers is less than the max_containers
        while len(self.running_containers) >= self.max_containers:  # Check status of running containers
            time.sleep(5)  # Wait 5 seconds before checking the containers again

            for container_name in self.running_containers[:]:  # Iterate over a copy of the list
                try:
                    # If this returns a value the container is still running
                    container = self.client.containers.get(container_name)
                    # If we caught the container as it was shutting down before being removed
                    if container.status == 'exited':
                        print(f"Container '{container_name}' completed @ {datetime.now().strftime('%H:%M:%S')}")
                        self.running_containers.remove(container_name)
                except docker.errors.NotFound:
                    # Container may have already been removed (we declared the '--rm' flag)
                    self.running_containers.remove(container_name)
                    print(f"Container '{container_name}' completed and removed @ {datetime.now().strftime('%H:%M:%S')}")

    def run(self):
        manga_list = self.read_manga_list()

        if not manga_list:
            print("No Urls provided in file.")
            return
        # Iterate through the list of manga and spin up to the max number of containers to download from at a time
        for manga_url in manga_list:
            container_name = valid_container_name(manga_url)
            command_args = f"{manga_url} {self.defaults}"

            name = self.start_download(container_name, command_args)
            if name:
                self.running_containers.append(name)

            self.manage_containers()
