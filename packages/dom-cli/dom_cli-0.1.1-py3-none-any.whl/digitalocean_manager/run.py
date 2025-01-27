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

import paramiko
import os


class RemoteScriptExecutor:
    def __init__(self, droplet_ip, ssh_key_path):
        self.droplet_ip = droplet_ip
        self.ssh_key_path = ssh_key_path
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def execute_script(self, script_path):
        """Load a script from disk and execute it remotely."""
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script {script_path} not found.")

        with open(script_path, 'r') as file:
            script = file.read()

        try:
            # Connect to the droplet
            self.ssh_client.connect(self.droplet_ip, key_filename=self.ssh_key_path)

            # Execute the script
            stdin, stdout, stderr = self.ssh_client.exec_command(script)
            print(stdout.read().decode())
            print(stderr.read().decode())
        finally:
            self.ssh_client.close()
