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

import json

from digitalocean_manager.config import Config
from digitalocean_manager.client import DigitalOceanClient


class SSHKeyManager:

    def __init__(self):
        self.config = Config()
        self.client = DigitalOceanClient().get_client()

    def list(self) -> None:
        """List all SSH keys."""
        try:
            resp = self.client.ssh_keys.list()
            if 'ssh_keys' in resp:
                for ssh_key in resp['ssh_keys']:
                    self.display(ssh_key)
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error listing SSH keys: {e}")

    def info(self, ssh_key_id: int) -> None:
        """Get raw information about an SSH key."""
        try:
            resp = self.client.ssh_keys.get(ssh_key_id)
            if 'ssh_key' in resp:
                print(json.dumps(resp['ssh_key'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting SSH key info: {e}")

    def display(self, ssh_key: dict) -> None:
        """Display SSH key information."""
        print(
            f"ID: {ssh_key['id']}, "
            f"Name: {ssh_key['name']}, "
            f"Fingerprint: {ssh_key['fingerprint']}"
        )