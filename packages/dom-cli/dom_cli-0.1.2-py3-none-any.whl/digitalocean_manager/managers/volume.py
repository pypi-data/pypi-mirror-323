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
from digitalocean_manager.template import volume_template, raw_volume_templates


class VolumeManager:
    """
    A class to manage volumes in DigitalOcean.

    Attributes:
        config (Config): Configuration object to handle settings and configurations.
        client (Client): DigitalOcean API client instance.
        action_manager (ActionManager): ActionManager instance to handle actions like attach/detach volumes.
    """

    def __init__(self):
        """
        Initialize the VolumeManager with the necessary configurations and client connections.
        """
        self.config = Config()
        self.client = DigitalOceanClient().get_client()
        self.action_manager = ActionManager()

    def create(
        self,
        template_name: str,
        volume_name: str,
        tags: tuple,
        dry_run: bool,
    ) -> None:
        """
        Create a new volume.

        Args:
            template_name (str): The name of the volume template to use.
            volume_name (str): The name for the new volume.
            tags (tuple): Tags to be applied to the new volume.
            dry_run (bool): Whether to simulate the creation process and print the request JSON.

        Raises:
            Exception: If there is an error creating the volume.

        This method sends a request to create a volume using the provided template name, volume name,
        tags, and region. If dry_run is True, it prints the request payload instead of sending the request.
        """
        try:
            req = volume_template(template_name, volume_name, tags)
            if dry_run:
                print(json.dumps(req, indent=self.config.json_indent))
            else:
                resp = self.client.volumes.create(body=req)
                if 'volume' in resp:
                    self.display(resp['volume'])
                else:
                    self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error creating volume: {e}")

    def list(self) -> None:
        """
        List all volumes in the specified region.

        Raises:
            Exception: If there is an error retrieving the list of volumes.

        This method retrieves and displays all volumes in the configured region.
        It prints information about each volume found.
        """
        try:
            resp = self.client.volumes.list(region=self.config.digitalocean_region)
            if 'volumes' in resp:
                for volume in resp['volumes']:
                    self.display(volume)
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error listing volumes: {e}")

    def delete(self, volume_id: str) -> None:
        """
        Delete a volume.

        Args:
            volume_id (str): The ID of the volume to delete.

        Raises:
            AssertionError: If the volume is protected.
            Exception: If there is an error deleting the volume.

        This method deletes the specified volume, after verifying that it is not protected.
        If the volume is protected, an assertion error is raised.
        """
        try:
            assert volume_id not in self.config.protected_volumes, "Volume is protected."
            self.client.volumes.delete(volume_id)
        except Exception as e:
            print(f"Error deleting volume: {e}")

    def info(self, volume_id: str) -> None:
        """
        Get detailed information about a specific volume.

        Args:
            volume_id (str): The ID of the volume to retrieve information about.

        Raises:
            Exception: If there is an error retrieving volume information.

        This method fetches and prints detailed information about the specified volume in JSON format.
        """
        try:
            resp = self.client.volumes.get(volume_id)
            if 'volume' in resp:
                print(json.dumps(resp['volume'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting volume info: {e}")
    
    def attach(self, volume_name: str, droplet_id: int) -> None:
        """
        Attach a volume to a droplet.

        Args:
            volume_name (str): The name of the volume to attach.
            droplet_id (int): The ID of the droplet to attach the volume to.

        Raises:
            Exception: If there is an error attaching the volume.

        This method attaches a volume to the specified droplet, and tracks the action status.
        If the action is successful, it displays the action details and pings the action ID.
        """
        try:
            req = {
                'type': 'attach',
                'volume_name': volume_name,
                'droplet_id': droplet_id,
                'region': self.config.digitalocean_region,
                'tags': ['env:dev', 'app:dom'],
            }
            resp = self.client.volume_actions.post(body=req)
            if 'action' in resp:
                action = resp['action']
                self.action_manager.display(action)
                self.action_manager.ping(action['id'])
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error attaching volume: {e}")

    def detach(self, volume_name: str, droplet_id: int) -> None:
        """
        Detach a volume from a droplet.

        Args:
            volume_name (str): The name of the volume to detach.
            droplet_id (int): The ID of the droplet from which to detach the volume.

        Raises:
            AssertionError: If the droplet is protected.
            Exception: If there is an error detaching the volume.

        This method detaches a volume from the specified droplet, and tracks the action status.
        If the action is successful, it displays the action details and pings the action ID.
        """
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
            req = {
                'type': 'detach',
                'volume_name': volume_name,
                'droplet_id': droplet_id,
                'region': self.config.digitalocean_region,
            }
            resp = self.client.volume_actions.post(body=req)
            if 'action' in resp:
                action = resp['action']
                self.action_manager.display(action)
                self.action_manager.ping(action['id'])
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error detaching volume: {e}")

    def display(self, volume: dict) -> None:
        """
        Display information about a volume.

        Args:
            volume (dict): The volume object containing details about the volume.

        This method prints key information about the volume, including its ID, name, size,
        description, and associated droplet ID.
        """
        print(
            f"ID: {volume['id']}, "
            f"Name: {volume['name']}, "
            f"Size: {volume['size_gigabytes']}, "
            f"Description: {volume['description']}, "
            f"DropletID: {self._volume_droplet_id(volume)}"
        )
    
    def templates(self) -> None:
        """
        List all available volume templates.

        Raises:
            Exception: If there is an error retrieving the templates.

        This method retrieves and prints all available volume templates in JSON format.
        """
        try:
            templates = raw_volume_templates()
            print(json.dumps(templates, indent=self.config.json_indent))
        except Exception as e:
            print(f"Error reading templates from: {e}")
    
    def _volume_droplet_id(self, volume: dict) -> int:
        """
        Retrieve the droplet ID associated with a volume.

        Args:
            volume (dict): The volume object containing droplet IDs.

        Returns:
            int: The ID of the droplet associated with the volume, or 'None' if no droplet is associated.

        This method checks if the volume is associated with any droplet and returns the droplet ID.
        If no droplet is associated, it returns 'None'.
        """
        return volume['droplet_ids'][0] if volume['droplet_ids'] else 'None'