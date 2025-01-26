# run_on_vastai_decorator.py

import sys
import os
import json
import ast
import shutil
import asyncio
import logging
import pickle
import tarfile
from pathlib import Path
from functools import wraps
from pathlib import Path
import textwrap, shlex
import tarfile
import tempfile
from typing import Union
from .requirements import Requirements

# Reuse your existing dep_tracker logic
from .dep_tracker import (
    _collect_dependencies_recursively,
    _copy_local_files_to_output,
    _write_requirements_txt
)

# Import your Instance class from instance.py
from .instance import Instance

logger = logging.getLogger(__name__)

def run_on_vastai(output_dir="pruned_codebase", include_files=None, additional_reqs=None, **vastai_requirements):
    """
    Decorator that:
      - Analyzes the decorated function's module (and any local modules it imports).
      - Copies those local .py files to `output_dir`.
      - Writes a versioned requirements.txt with external dependencies.
      - Launches/gets a VastAI instance (per 'vastai_requirements').
      - SCPs the pruned code + requirements.txt to the instance.
      - Installs the requirements.
      - **Executes** the function on the remote instance.
      - **Captures** the return value by pickling it remotely, 
        transferring it back, and unpickling locally.

    Usage:
        @run_on_vastai(gpu_name="RTX_2080_Ti", price=0.5)
        def my_func(...):
            return [1,2,3]
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1) Determine the .py file where `func` is defined
            module_file = Path(sys.modules[func.__module__].__file__).resolve()
            project_root = module_file.parent

            # 2) Collect local dependencies
            visited_local = set()
            external_libs = set()
            _collect_dependencies_recursively(
                file_path=module_file,
                project_root=project_root,
                visited_local=visited_local,
                external_libs=external_libs
            )

            # 3) Copy local files into output_dir
            _copy_local_files_to_output(visited_local, project_root, output_dir)

            # 4) Write the pinned requirements
            _write_requirements_txt(external_libs, output_dir, additional_reqs)

            # 5) We'll do the VastAI steps in an async function
            # def sync_run_remote():
            #     return asyncio.run(_run_on_vastai_async(
            #         func, module_file, output_dir, vastai_requirements,
            #         args, kwargs, include_files
            #     ))

            # Return whatever that async function returns (the unpickled result)
            return _run_on_vastai_sync(func, module_file, output_dir, vastai_requirements,
                    args, kwargs, include_files)

        return wrapper
    return decorator


async def _run_on_vastai_async(func, module_file, output_dir, vastai_requirements, args, kwargs, include_files):
    """Internal async method to:
       - Launch/get the VastAI instance
       - Upload pruned code
       - Install deps
       - Run `func(*args, **kwargs)` remotely
       - Pickle & compress the return value
       - Download & unpickle the result
       - Return it
    """
    logger.info(f"[Decorator] Creating or retrieving VastAI instance with {vastai_requirements}")
    instance = await Instance.a_from_requirements(vastai_requirements)
    logger.info(f"[Decorator] Acquired VastAI instance: {instance}")

    # ZIP local pruned code
    code_zip = f"{output_dir}.zip"
    shutil.make_archive(output_dir, 'zip', output_dir)

    # 1) SCP pruned code + zip => remote
    instance.scp_local_file_to_instance(code_zip, code_zip)
    remote_zip = os.path.basename(code_zip)  # e.g. "pruned_codebase.zip"
    remote_pruned_code_dir = remote_zip.removesuffix(".zip")  # e.g. "pruned_codebase"
    # remote_dir = "/root/workspace"

    # 2) Unzip code
    # First create a 'remote_pruned_code_dir' directory
    instance.run_command(f"mkdir -p {remote_pruned_code_dir}")
    # First install unzip
    instance.run_command("apt-get update && apt-get install -y unzip")
    unzip_cmd = f"cd {remote_pruned_code_dir} && unzip -o ../{remote_zip}"
    instance.run_command(unzip_cmd)

    # 3) pip install -r requirements.txt
    remote_requirements_path = f"{remote_pruned_code_dir}/requirements.txt"
    install_cmd = f"pip install -r {remote_requirements_path}"
    instance.run_command(install_cmd)

    # 4) Compress and transfer additional files``
    if include_files:
        _compress_and_transfer_additional_files(instance, include_files, remote_pruned_code_dir)


    # 4) Run the function remotely, capturing the return value

    # We'll store it as function_output.pkl => then compress => function_output.tar.gz
    result_pkl = "function_output.pkl"
    result_tar = "function_output.tar.gz"

    # We'll do naive JSON for the arguments, then call a short Python snippet that:
    #   - imports the function
    #   - calls it
    #   - pickles the result
    args_kwargs = json.dumps([args, kwargs])
    args_kwargs_escaped = args_kwargs.replace('"', '\\"')

    module_name = os.path.splitext(os.path.basename(module_file))[0]
    func_name = func.__name__

    # 1) Build the actual Python code you want to run
    snippet = textwrap.dedent(f"""
    import json, pickle
    from {remote_pruned_code_dir}.{module_name} import {func_name}

    args, kwargs = json.loads({repr(args_kwargs)})
    retval = {func_name}(*args, **kwargs)

    with open({repr(result_pkl)}, "wb") as f:
        pickle.dump(retval, f, protocol=4)
    """)

    # Let Python handle the quoting for the shell
    remote_cmd = f"python -c {shlex.quote(snippet)}"


    logger.info(f"[Decorator] Running remote command to produce function output: {remote_cmd}")
    success, output = instance.run_command(remote_cmd)
    if not success:
        logger.error("[Decorator] Remote function execution failed. See logs.")
        return None

    # 5) Compress the result file
    compress_cmd = f"tar -czf {result_tar} {result_pkl}"
    instance.run_command(compress_cmd)

    # 6) Download result_tar => local
    local_result_tar_path = os.path.join(output_dir, result_tar)  # Ensure full path
    instance.scp_remote_file_to_local(
        remote_filepath=result_tar,
        local_path=local_result_tar_path  # Pass full path here
    )

    # 7) Decompress locally
    with tarfile.open(local_result_tar_path, "r:gz") as tar:
        tar.extractall(path=output_dir)

    # 8) Load the pickle => final return value
    local_pkl_path = os.path.join(output_dir, result_pkl)
    with open(local_pkl_path, "rb") as f:
        returned_value = pickle.load(f)

    logger.info("[Decorator] Successfully retrieved remote return value.")
    return returned_value



def _run_on_vastai_sync(func, module_file, output_dir, vastai_requirements: Union[Requirements, dict], args, kwargs, include_files):
    """Internal async method to:
       - Launch/get the VastAI instance
       - Upload pruned code
       - Install deps
       - Run `func(*args, **kwargs)` remotely
       - Pickle & compress the return value
       - Download & unpickle the result
       - Return it
    """
    logger.info(f"[Decorator] Creating or retrieving VastAI instance with {vastai_requirements}")
    instance = Instance.from_requirements(vastai_requirements)
    logger.info(f"[Decorator] Acquired VastAI instance: {instance}")

    # ZIP local pruned code
    code_zip = f"{output_dir}.zip"
    shutil.make_archive(output_dir, 'zip', output_dir)

    # 1) SCP pruned code + zip => remote
    instance.scp_local_file_to_instance(code_zip, code_zip)
    remote_zip = os.path.basename(code_zip)  # e.g. "pruned_codebase.zip"
    remote_pruned_code_dir = remote_zip.removesuffix(".zip")  # e.g. "pruned_codebase"
    # remote_dir = "/root/workspace"

    # 2) Unzip code
    # First create a 'remote_pruned_code_dir' directory
    instance.run_command(f"mkdir -p {remote_pruned_code_dir}")
    # First install unzip
    instance.run_command("apt-get update && apt-get install -y unzip")
    unzip_cmd = f"cd {remote_pruned_code_dir} && unzip -o ../{remote_zip}"
    instance.run_command(unzip_cmd)

    # 3) pip install -r requirements.txt
    remote_requirements_path = f"{remote_pruned_code_dir}/requirements.txt"
    # install_cmd = f"pip install -r {remote_requirements_path}"
    # INstall 1 by 1 so that a single package failure doesn't stop the rest
    install_cmd = f"cat {remote_requirements_path} | xargs -n 1 pip install"
    instance.run_command(install_cmd)

    # 4) Compress and transfer additional files``
    if include_files:
        _compress_and_transfer_additional_files(instance, include_files, remote_pruned_code_dir)


    # 4) Run the function remotely, capturing the return value

    # We'll store it as function_output.pkl => then compress => function_output.tar.gz
    result_pkl = "function_output.pkl"
    result_tar = "function_output.tar.gz"

    # We'll do naive JSON for the arguments, then call a short Python snippet that:
    #   - imports the function
    #   - calls it
    #   - pickles the result
    args_kwargs = json.dumps([args, kwargs])
    args_kwargs_escaped = args_kwargs.replace('"', '\\"')

    module_name = os.path.splitext(os.path.basename(module_file))[0]
    func_name = func.__name__

    # 1) Build the actual Python code you want to run
    snippet = textwrap.dedent(f"""
    import json, pickle
    from {remote_pruned_code_dir}.{module_name} import {func_name}

    args, kwargs = json.loads({repr(args_kwargs)})
    retval = {func_name}(*args, **kwargs)

    with open({repr(result_pkl)}, "wb") as f:
        pickle.dump(retval, f, protocol=4)
    """)

    # Let Python handle the quoting for the shell
    remote_cmd = f"python -c {shlex.quote(snippet)}"


    logger.info(f"[Decorator] Running remote command to produce function output: {remote_cmd}")
    success, output = instance.run_command(remote_cmd)
    if not success:
        logger.error("[Decorator] Remote function execution failed. See logs.")
        return None

    # 5) Compress the result file
    compress_cmd = f"tar -czf {result_tar} {result_pkl}"
    instance.run_command(compress_cmd)

    # 6) Download result_tar => local
    local_result_tar_path = os.path.join(output_dir, result_tar)  # Ensure full path
    instance.scp_remote_file_to_local(
        remote_filepath=result_tar,
        local_path=local_result_tar_path  # Pass full path here
    )

    # 7) Decompress locally
    with tarfile.open(local_result_tar_path, "r:gz") as tar:
        tar.extractall(path=output_dir)

    # 8) Load the pickle => final return value
    local_pkl_path = os.path.join(output_dir, result_pkl)
    with open(local_pkl_path, "rb") as f:
        returned_value = pickle.load(f)

    logger.info("[Decorator] Successfully retrieved remote return value.")
    return returned_value



def _compress_and_transfer_additional_files(instance, include_paths, remote_dir):
    """
    Compress each additional file or directory individually, check if it exists on the remote,
    and only transfer it if it is missing or outdated.

    Args:
        instance: Instance object for VastAI.
        include_paths: List of file or directory paths to compress and transfer.
        remote_dir: Directory on the VastAI instance where the files will be decompressed.
    """
    for path in include_paths:
        local_path = Path(path).resolve()
        if not local_path.exists():
            raise ValueError(f"Path '{local_path}' does not exist.")

        # Create a temporary tarball for the individual file/directory
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as temp_tar:
            tar_path = temp_tar.name  # Local tarball path

        try:
            # Compress the file or directory
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(local_path, arcname=local_path.name)
            logger.info(f"[Decorator] Compressed {local_path} into {tar_path}")

            # Define the remote tarball path
            remote_tar_path = f"{remote_dir}/{local_path.name}.tar.gz"

            # Check if the tarball already exists on the remote instance
            remote_status = check_remote_path(instance, remote_tar_path)

            # Compare file sizes to decide if we need to transfer
            local_size = os.path.getsize(tar_path)
            if remote_status["exists"] and remote_status["is_file"] and remote_status["size"] == local_size:
                logger.info(f"[Decorator] Remote file {remote_tar_path} is up-to-date. Skipping transfer.")
                continue

            # Transfer the tarball to the VastAI instance
            instance.scp_local_file_to_instance(tar_path, remote_tar_path)
            logger.info(f"[Decorator] Transferred {tar_path} to {remote_tar_path} on the instance.")

            # Decompress the tarball on the instance
            decompress_cmd = f"tar -xzf {remote_tar_path} -C {remote_dir}"
            instance.run_command(decompress_cmd)
            logger.info(f"[Decorator] Decompressed {remote_tar_path} on the instance at {remote_dir}")

            # Clean up the remote tarball
            # instance.run_command(f"rm {remote_tar_path}")
            # logger.info(f"[Decorator] Removed remote tarball {remote_tar_path}")

        finally:
            # Clean up the local tarball
            if os.path.exists(tar_path):
                os.remove(tar_path)
                logger.info(f"[Decorator] Removed local tarball {tar_path}")


def check_remote_path(instance, remote_path):
    """
    Check if a remote path exists and is a file or directory. If it's a file, return its size.

    Args:
        instance: VastAI instance object.
        remote_path (str): Path on the remote instance to check.

    Returns:
        dict: {
            "exists": bool,
            "is_file": bool,
            "size": int (file size in bytes, or None if not a file),
            "is_dir": bool
        }
    """
    cmd = f"""
    if [ -e {remote_path} ]; then
        if [ -f {remote_path} ]; then
            echo "file $(stat -c%s {remote_path})";
        elif [ -d {remote_path} ]; then
            echo "dir";
        else
            echo "other";
        fi;
    else
        echo "none";
    fi
    """
    stdin, stdout, stderr = instance.client.exec_command(cmd)
    result = stdout.read().decode().strip()

    if result.startswith("file"):
        _, size = result.split()
        return {"exists": True, "is_file": True, "size": int(size), "is_dir": False}
    elif result == "dir":
        return {"exists": True, "is_file": False, "size": None, "is_dir": True}
    elif result == "none":
        return {"exists": False, "is_file": False, "size": None, "is_dir": False}
    else:
        # Unexpected result
        return {"exists": False, "is_file": False, "size": None, "is_dir": False}
