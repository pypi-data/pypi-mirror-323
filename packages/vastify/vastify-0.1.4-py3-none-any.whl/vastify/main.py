import os
from functools import wraps

# Define the global activity variable name
ACTIVITY_VAR = "VASTAI_DECORATED_CODE_ACTIVE"

def vast_run(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Set the activity variable to indicate activity
            os.environ[ACTIVITY_VAR] = "true"
            print(f"[Decorator] {ACTIVITY_VAR} set to true.")

            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Reset the activity variable to indicate no activity
            os.environ[ACTIVITY_VAR] = "false"
            print(f"[Decorator] {ACTIVITY_VAR} set to false.")

    return wrapper

# Example usage
@vast_run
def gpu_task(data):
    print("Performing GPU-intensive task...")
    # Simulate some processing
    import time
    time.sleep(10)
    print("Task complete.")
