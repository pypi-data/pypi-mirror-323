import numpy as np
from tqdm import tqdm

def test_func(N=10_000):
    """
    Example function that creates and returns a large NumPy array.
    """

    # We'll build a simple 1D array where arr[i] = i^2
    # This for-loop will have a lot of prints from tqdm if N=10000
    data = []
    for i in tqdm(range(N)):
        data.append(i ** 2)

    # Convert to a numpy array
    arr = np.array(data, dtype=np.int64)
    return arr