# Copyright 2025 Cloutfit.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import paramiko


class RemoteScriptExecutor:
    """
    A class for executing scripts remotely on a droplet via SSH.

    This class connects to a remote droplet using SSH and executes a script on it.
    The connection is established using the provided IP address and SSH key path.

    Attributes:
        droplet_ip (str): The IP address of the droplet to connect to.
        ssh_key_path (str): The path to the SSH private key used for authentication.
        ssh_client (paramiko.SSHClient): The paramiko SSH client used for the connection.
    """

    def __init__(self, droplet_ip: str, ssh_key_path: str):
        """
        Initializes the RemoteScriptExecutor instance.

        This method sets up the droplet IP address, the SSH key path for authentication,
        and initializes the SSH client.

        Args:
            droplet_ip (str): The IP address of the droplet.
            ssh_key_path (str): The path to the SSH private key used for authentication.

        Raises:
            ValueError: If the SSH key path does not exist or is not a file.
        """
        if not os.path.exists(ssh_key_path) or not os.path.isfile(ssh_key_path):
            raise ValueError(f"SSH key file '{ssh_key_path}' does not exist or is not a valid file.")

        self.droplet_ip = droplet_ip
        self.ssh_key_path = ssh_key_path
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def execute_script(self, script_path: str) -> None:
        """
        Loads a script from disk and executes it remotely on the droplet.

        This method reads the provided script from disk and connects to the remote
        droplet using SSH to execute it.

        Args:
            script_path (str): The path to the script to execute.

        Raises:
            FileNotFoundError: If the specified script does not exist.
            Exception: If there is an error during SSH connection or script execution.
        """
        # Check if the script exists
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script {script_path} not found.")

        # Read the script content from the file
        with open(script_path, 'r') as file:
            script = file.read()

        try:
            # Connect to the droplet using SSH
            self.ssh_client.connect(self.droplet_ip, key_filename=self.ssh_key_path)

            # Execute the script on the remote droplet
            stdin, stdout, stderr = self.ssh_client.exec_command(script)

            # Output the result and any errors
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"Error: {err}")
        except Exception as e:
            raise Exception(f"Failed to execute script on droplet {self.droplet_ip}: {e}")
        finally:
            # Ensure the SSH connection is closed
            self.ssh_client.close()