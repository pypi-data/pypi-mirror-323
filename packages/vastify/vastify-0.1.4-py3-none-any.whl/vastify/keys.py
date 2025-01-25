import os
import platform
import pathlib

def get_private_key_path():
    """
    Detects the runtime environment and returns the appropriate private key path.
    """
    # Detect if running in a Docker container
    in_docker = False
    if os.path.exists("/proc/self/cgroup"):
        with open("/proc/self/cgroup", "r") as f:
            in_docker = any(
                "docker" in line or "kubepod" in line for line in f)

    # Check the OS type
    os_name = platform.system()

    # Determine the path
    if in_docker:
        # Typical Docker container private key path
        private_key_path = "/root/.ssh/id_rsa"
    elif os_name == "Darwin":  # macOS
        print("macOS detected.")
        # macOS private key path
        private_key_path = str(pathlib.Path.home() / ".ssh" / "id_rsa")
    else:
        # Default fallback for other environments
        private_key_path = str(pathlib.Path.home() / ".ssh" / "id_rsa")

    return private_key_path


# Example usage in your script
PRIVATE_KEY_PATH = get_private_key_path()