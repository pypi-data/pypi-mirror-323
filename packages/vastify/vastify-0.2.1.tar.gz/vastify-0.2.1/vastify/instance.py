from .search import get_instance_state, get_active_or_launch_instance
import logging
import asyncio
from .patched_vastai import VastAI
import paramiko
from .keys import PRIVATE_KEY_PATH
import os
from .persist import save_pickle, load_pickle
import subprocess
import time
from .instance_state import InstanceState
from .requirements import Requirements
from typing import Union

logger = logging.getLogger(__name__)

vast_sdk = VastAI(
    api_key=os.environ.get("VASTAI_API_KEY"))


class Instance:
    '''Class that represents a VastAI instance.

    Loads either an existing instance or launches a new one based on the requirements. Automatically waits until the instance is fully started. Deletes the vastai instance when the object is garbage collected.

    Example usage:
        ```python
        requirements = dict(
            gpu_name="RTX_2080_Ti",
            price=0.5,
            disk=100.0,
            image='hakbijl/autopar-tgn:latest',
            num_gpus='1',
            regions=['Europe', 'North_America', 'World'],
            env='-p 70000:8000')


        instance = await Instance.from_requirements(requirements)
        print(instance)
        ```

            '''

    def __init__(self, instance_id, requirements=None):
        self.instance_id = instance_id
        self.requirements = requirements
        instance_state = get_instance_state(instance_id)
        self.ssh_addr = instance_state.ssh_host
        self.ssh_port = int(instance_state.ssh_port)
        self.ssh_user = 'root'

        print(self.get_state())

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(
                self.ssh_addr,
                port=self.ssh_port,
                username=self.ssh_user,
                key_filename=PRIVATE_KEY_PATH,
                # pkey=key,
                banner_timeout=10000
            )
            
            # 1) Invoke a shell channel (this requests a pty by default).
            channel = self.client.invoke_shell()

            # 2) Wait until it’s ready to receive input
            time.sleep(1)

            # 3) Send the touch command
            channel.send("touch ~/.no_auto_tmux\n")
            time.sleep(1)

            # 4) Exit
            channel.send("exit\n")
            time.sleep(1)

            channel.close()
        except Exception as e:
            logger.error(
                f"Could not connect to instance {self.instance_id} with error: {e}. Destroying instance.")
            if 'Unable to connect to port' in str(e):
                self.blacklist_instance()

            self.terminate_instance()
            return Instance.from_requirements(self.requirements)

        
        
        # Always set the inactivity monitor
        # self.set_auto_destroy_when_inactive()

    def blacklist_instance(self):
        logger.error(f"Blacklisting {self.get_state()['Machine']}")
        # Blacklist the address
        # Load current blacklist
        blacklist = load_pickle('blacklist', default=set())
        blacklist.add(self.get_state()['Machine'])
        save_pickle(blacklist, 'blacklist')
        
    def set_auto_destroy_when_inactive(self, n: int = 300):
        '''The instance will be destrooyed automatically when it becomes inactive for N minutes. Code with the run_vastai decorator let's the instance know that it is active.
        
            Args:
            - n: The number of seconds to wait before destroying the instance.'''
        try:
            self.scp_local_file_to_instance("/Users/sethvanderbijl/PitchAI Code/run-on-vastai/run_on_vastai/inactivity_monitor.py", "inactivity_monitor.py")
        except Exception as e:
            logger.error(f"Error uploading inactivity monitor to instance: {e}. Instance will be deleted to avoid incurring costs.")
            self.blacklist_instance()
            self.terminate_instance()
            raise e
        
        # Activate the inactivity monitor
        succes, output = self.run_command(
            "nohup python3 inactivity_monitor.py > monitor.log 2>&1 &"
        )

        if not succes:
            logger.error(f"Error starting inactivity monitor on instance: {output}. Instance will be deleted to avoid incurring costs.")
            self.blacklist_instance()
            self.terminate_instance()
        logger.warning(f"Activity monitor set. Instance {self.instance_id} will be destroyed after {n} seconds of inactivity.")
        

    def get_state(self):
        return get_instance_state(self.instance_id)

    def run_command(self, command: str):
        logger.info(f"Running command on instance {self.instance_id}: {command}")
        stdin, stdout, stderr = self.client.exec_command(command)
        
        # read both streams once
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        
        # optional: get the return code
        exit_status = stdout.channel.recv_exit_status()

        # log them or decide success/failure
        if exit_status != 0:
            logger.error(f"[Instance {self.instance_id}] Command failed with exit status {exit_status}")
            logger.error(f"STDERR:\n{stderr_data}")
            logger.error(f"STDOUT:\n{stdout_data}")
            return False, stderr_data  # or some combined info

        # If no errors, log the stdout
        logger.info(f"STDOUT:\n{stdout_data}")
        return True, stdout_data

    
    def terminate_instance(self):
        '''Gracefully removes the instance from VastAI. Closes connnections.'''
        logger.info(
            f"Instance is getting garbage collected, terminating it {self.instance_id}")
        try:
            self.client.close()
            vast_sdk.destroy_instance(id=self.instance_id)
        except Exception as e:
            logger.error(
                f"Error when terminating instance {self.instance_id}: {e}")

    # def __del__(self):
    #     '''Destructor that terminates the instance when the object is garbage collected or out-of-scope or manually deleted or when the program exits.'''
    #     self.terminate_instance()
        

    def scp_local_file_to_instance(self, local_filepath: str, remote_filepath: str):
        """
        Transfer a file to the remote instance using scp from the local machine.
        """
        sftp = self.client.open_sftp()
        sftp.put(local_filepath, remote_filepath, callback=print_totals)
        # sftp.close()


    def scp_remote_file_to_local(self, remote_filepath: str, local_path: str):
        """
        Download a file from the instance using SCP.

        Args:
            remote_filepath (str): Path to the remote file to download.
            local_path (str): Full local path (including filename) where the file should be saved.
        """
        sftp = self.client.open_sftp()
        local_dir = os.path.dirname(local_path)  # Get directory part of the local path
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)  # Ensure the local directory exists
        sftp.get(remote_filepath, local_path)  # Download the file to the specified local path
        sftp.close()

    def get_remote_file_size(self, remote_path):
        """
        Check the size of a remote file on the instance.

        Args:
            remote_path (str): Path to the remote file.

        Returns:
            int: File size in bytes, or None if the file does not exist.
        """
        try:
            stdin, stdout, stderr = self.client.exec_command(f"stat -c%s {remote_path}")
            size = stdout.read().strip()
            if size.isdigit():
                return int(size)
        except Exception as e:
            logger.warning(f"[Instance] Could not get size for {remote_path}: {e}")
        return None
    
    @staticmethod
    def from_requirements(requirements: Union[Requirements, dict]):
        if isinstance(requirements, dict):
            requirements = Requirements(**requirements)
        instance_id = get_active_or_launch_instance(requirements)

        Instance.wait_until_started(instance_id)

        return Instance(instance_id, requirements)


    @staticmethod
    async def a_from_requirements(requirements: Union[Requirements, dict]):
        if isinstance(requirements, dict):
            requirements = Requirements(**requirements)
        instance_id = get_active_or_launch_instance(requirements)

        await Instance.await_until_started(instance_id)

        return Instance(instance_id, requirements)
    
    @staticmethod
    def wait_until_started(instance_id: str, timeout: int = 300):
        '''Waiter that waits until the instance is fully started.

            Args:
            - instance_id: The id of the instance to wait for.
            - timeout: The maximum time to wait in seconds.'''
        start_time = time.time()
        instance_state = get_instance_state(instance_id)
        while instance_state.actual_status != 'running':
            logger.info('Instance is still starting, waiting...')
            time.sleep(2)
            instance_state = get_instance_state(instance_id)
            if time.time() - start_time > timeout:
                logger.error(f"Instance did not start in {timeout} seconds.")
                return None
        logger.info(
            f'Instance finished starting, new state: {instance_state.actual_status}')
        # Still wait 5 seconds to not overload the things
        time.sleep(5)
        return instance_id

    @staticmethod
    async def await_until_started(instance_id: str, timeout: int = 300):
        '''Async waiter that waits until the instance is fully started.

            Args:
            - instance_id: The id of the instance to wait for.
            - timeout: The maximum time to wait in seconds.'''
        start_time = asyncio.get_event_loop().time()
        instance_state = get_instance_state(instance_id)
        while instance_state.actual_status != 'running':
            logger.info('Instance is still starting, waiting...')
            await asyncio.sleep(2)
            instance_state = get_instance_state(instance_id)
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.error(f"Instance did not start in {timeout} seconds.")
                return None
        logger.info(
            f'Instance finished starting, new state: {instance_state.actual_status}')
        # Still wait 5 seconds to not overload the things
        await asyncio.sleep(5)
        return instance_id

    def __str__(self):
        return f"Instance {self.instance_id} at {self.ssh_addr}:{self.ssh_port} with keyfile {PRIVATE_KEY_PATH}"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    requirements = dict(
        gpu_name="RTX_2080_Ti",
        price=0.5,
        disk=100.0,
        image='hakbijl/autopar-tgn:latest',
        num_gpus='1',
        regions=['Europe', 'North_America', 'World'],
        env='-p 70000:8000')

    async def main():
        instance = await Instance.from_requirements(requirements)

        print(instance)


        

        await asyncio.sleep(10000)

    asyncio.run(main())


def print_totals(transferred, toBeTransferred):
    print(f"Transferred: ({round((transferred/toBeTransferred)*100, 1)}%) {transferred}\tOut of: {toBeTransferred}", end="\r")