from .decorator import run_on_vastai
from .test_code import test_func
import logging

@run_on_vastai(output_dir="pruned_codebase",
               gpu_name="RTX 2080 Ti",
               price=0.25,
               disk=100.0,
               image='python:3.10-slim',
               num_gpus='1',
               regions=['North_America','Europe', 'World'],
               env='-p 70000:8000')
def example_function():
    return test_func()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(name)s:%(lineno)d:%(message)s', level=logging.INFO)
    res = example_function()

    print("Result from test example function:", res)
