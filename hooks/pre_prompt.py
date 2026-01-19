import sys
import subprocess


def _get_preferred_client_type():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"

def is_compose_installed(client) -> bool:
    try:
        subprocess.run([client, "compose", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    client = _get_preferred_client_type()
    if not client or not is_compose_installed(client):
        print("WARNING: Compose is not installed. This project needs it to work.")
