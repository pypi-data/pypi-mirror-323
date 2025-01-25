import pickle
import os

def save_pickle(data, key, directory="pickles"):
    """
    Save data to a pickle file based on a key.
    """
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, f"{key}.pkl"), "wb") as f:
        pickle.dump(data, f)

def load_pickle(key, directory="pickles", default=None):
    """
    Load and return data from a pickle file based on a key.
    """
    if not os.path.exists(os.path.join(directory, f"{key}.pkl")):
        return default
    with open(os.path.join(directory, f"{key}.pkl"), "rb") as f:
        return pickle.load(f)
