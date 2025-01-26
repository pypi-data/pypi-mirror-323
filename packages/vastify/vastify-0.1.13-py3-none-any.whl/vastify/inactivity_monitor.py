import os
import time
import subprocess

# Configurable timeout (in seconds)
INACTIVITY_TIMEOUT = 300  # 5 minutes
CHECK_INTERVAL = 30       # Check every 30 seconds
ACTIVITY_VAR = "VASTAI_DECORATED_CODE_ACTIVE"

def check_activity():
    """Check if the activity variable is set to true."""
    return os.environ.get(ACTIVITY_VAR) == "true"

def shutdown_instance():
    """Shutdown the instance."""
    print("No activity detected. Shutting down the instance...")
    subprocess.run(["shutdown", "-h", "now"])

def main():
    last_active_time = time.time()

    while True:
        # Check if activity has been detected
        if check_activity():
            # Reset the last activity time
            last_active_time = time.time()
            print(f"[Monitor] Activity detected. Timer reset to {last_active_time}.")

        # If no activity and timeout exceeded, shut down the instance
        elif time.time() - last_active_time > INACTIVITY_TIMEOUT:
            shutdown_instance()
            break

        # Wait before checking again
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
