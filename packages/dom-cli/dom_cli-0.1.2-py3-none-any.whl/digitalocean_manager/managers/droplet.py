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
from digitalocean_manager.managers.action import ActionManager
from digitalocean_manager.template import droplet_template, raw_droplet_templates


class DropletManager:
    """
    A class to manage droplets in DigitalOcean.

    Attributes:
        config (Config): Configuration object to handle settings and configurations.
        client (Client): DigitalOcean API client instance.
        action_manager (ActionManager): ActionManager instance to handle actions like create/start/stop droplets.
    """

    DROPLET_TYPES = {'cpu': 'droplets', 'gpu': 'gpus'} # Maps 'dom style' to DigitalOcean style for filtering droplets

    def __init__(self):
        """
        Initializes the DropletManager with the necessary configurations and client connections.
        """
        self.config = Config()
        self.client = DigitalOceanClient().get_client()
        self.action_manager = ActionManager()

    def create(
        self,
        template_name: str,
        droplet_name: str,
        keys: tuple,
        volumes: tuple,
        tags: tuple,
        cloud_config_name: str,
        dry_run: bool,
    ) -> None:
        """
        Creates a droplet from a specified template and with the given configurations.

        Args:
            template_name (str): The name of the droplet template (without extension).
            droplet_name (str): The name to assign to the new droplet.
            keys (tuple): SSH keys to associate with the droplet.
            volumes (tuple): Volumes to attach to the droplet.
            tags (tuple): Tags for the new droplet.
            cloud_config_name (str): The name of the cloud config file to use.
            dry_run (bool): Whether to display the droplet request as JSON without actually creating it.

        Raises:
            Exception: If any error occurs during the creation of the droplet.
        """
        try:
            req = droplet_template(
                template_name,
                droplet_name,
                keys,
                volumes,
                tags,
                cloud_config_name,
            )
            if dry_run:
                print(json.dumps(req, indent=self.config.json_indent))
            else:
                resp = self.client.droplets.create(body=req)
                if 'droplet' in resp:
                    self.display(resp['droplet'])
                    self.action_manager.ping(resp['links']['actions'][0]['id'])
                else:
                    self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error creating droplet: {e}")

    def list(self, droplet_type: str) -> None:
        """
        List all droplets of a specific type (CPU or GPU).

        Args:
            droplet_type (str): The type of droplet to list, either 'cpu' or 'gpu'.

        Raises:
            Exception: If any error occurs during listing of the droplets.
        """
        try:
            resp = self.client.droplets.list(type=DropletManager.DROPLET_TYPES[droplet_type])
            if 'droplets' in resp:
                for droplet in resp['droplets']:
                    if droplet['region']['slug'] == self.config.digitalocean_region:
                        self.display(droplet)
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error listing droplets: {e}")

    def stop(self, droplet_id: int) -> None:
        """
        Stop a droplet by sending a shutdown request.

        Args:
            droplet_id (int): The ID of the droplet to stop.

        Raises:
            Exception: If any error occurs during the stopping of the droplet.
        """
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
            req = {'type': 'shutdown'}
            resp = self.client.droplet_actions.post(droplet_id=droplet_id, body=req)
            if 'action' in resp:
                action = resp['action']
                self.action_manager.display(action)
                self.action_manager.ping(action['id'])
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error stopping droplet: {e}")
    
    def start(self, droplet_id: int) -> None:
        """
        Start a droplet by sending a power-on request.

        Args:
            droplet_id (int): The ID of the droplet to start.

        Raises:
            Exception: If any error occurs during the starting of the droplet.
        """
        try:
            req = {'type': 'power_on'}
            resp = self.client.droplet_actions.post(droplet_id=droplet_id, body=req)
            if 'action' in resp:
                action = resp['action']
                self.action_manager.display(action)
                self.action_manager.ping(action['id'])
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error starting droplet: {e}")

    def delete(self, droplet_id: int) -> None:
        """
        Delete a droplet.

        Args:
            droplet_id (int): The ID of the droplet to delete.

        Raises:
            Exception: If any error occurs during the deletion of the droplet.
        """
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
            self.client.droplets.destroy(droplet_id)
        except Exception as e:
            print(f"Error deleting droplet: {e}")

    def info(self, droplet_id: int) -> None:
        """
        Fetch and display raw information about a droplet.

        Args:
            droplet_id (int): The ID of the droplet for which to fetch information.

        Raises:
            Exception: If any error occurs during the fetching of droplet information.
        """
        try:
            resp = self.client.droplets.get(droplet_id)
            if 'droplet' in resp:
                print(json.dumps(resp['droplet'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting droplet info: {e}")
    
    def display(self, droplet: dict) -> None:
        """
        Display a human-readable summary of the droplet's information.

        Args:
            droplet (dict): The droplet information to display.
        """
        print(
            f"ID: {droplet['id']}, "
            f"Name: {droplet['name']}, "
            f"Region: {droplet['region']['slug']}, "
            f"Memory: {droplet['memory']}, "
            f"VCPUs: {droplet['vcpus']}, "
            f"Disk: {droplet['disk']}, "
            f"Status: {droplet['status']}, "
            f"PublicIP: {self._droplet_public_ip(droplet)}"
        )
    
    def templates(self) -> None:
        """
        List available droplet templates from the configuration.

        Raises:
            Exception: If any error occurs while reading templates.
        """
        try:
            templates = raw_droplet_templates()
            print(json.dumps(templates, indent=self.config.json_indent))
        except Exception as e:
            print(f"Error reading templates from: {e}")
    
    def _droplet_public_ip(self, droplet: dict) -> str:
        """
        Extract the public IP address of a droplet from its network information.

        Args:
            droplet (dict): The droplet information containing network details.

        Returns:
            str: The public IP address of the droplet, or 'None' if not found.
        """
        for network in droplet.get('networks', {}).get('v4', []):
            if network.get('type') == 'public':
                return network.get('ip_address')
        return 'None'