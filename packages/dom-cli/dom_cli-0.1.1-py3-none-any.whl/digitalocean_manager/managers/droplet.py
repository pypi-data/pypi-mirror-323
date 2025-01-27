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

    DROPLET_TYPES = {'cpu': 'droplets', 'gpu': 'gpus'}

    def __init__(self):
        self.config = Config()
        self.client = DigitalOceanClient().get_client()
        self.action_manager = ActionManager()

    def create(
            self,
            template_name: str, # Name of the droplet template without extension
            droplet_name: str, # Name for the new droplet
            keys: tuple, # ssh keys
            volumes: tuple, # Volumes to attach to the droplet
            tags: tuple, # Tags for the new droplet
            cloud_config_filename: str, # Name of the cloud config file
            dry_run: bool,
        ) -> None:
        """Create a droplet."""
        try:
            req = droplet_template(
                template_name,
                droplet_name,
                keys,
                volumes,
                tags,
                cloud_config_filename,
            )
            if dry_run:
                print(json.dumps(req, indent=self.config.json_indent))
            else:
                pass
                #resp = self.client.droplets.create(body=req)
                #if 'droplet' in resp:
                #    self.display(resp['droplet'])
                #    self.action_manager.ping(resp['links']['actions'][0]['id'])
                #else:
                #    self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error creating droplet: {e}")

    def list(self, droplet_type: str) -> None:
        """List all droplets."""
        try:
            resp = self.client.droplets.list(type=DropletManager.DROPLET_TYPES[droplet_type])
            if 'droplets' in resp:
                for droplet in resp['droplets']:
                    self.display(droplet)
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error listing droplets: {e}")

    def stop(self, droplet_id: int) -> None:
        """Stop a droplet."""
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
        """Start a droplet."""
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
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
        """Delete a droplet."""
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
            self.client.droplets.destroy(droplet_id)
        except Exception as e:
            print(f"Error deleting droplet: {e}")

    def info(self, droplet_id: int) -> None:
        """Get raw information about a droplet."""
        try:
            resp = self.client.droplets.get(droplet_id)
            if 'droplet' in resp:
                print(json.dumps(resp['droplet'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting droplet info: {e}")
    
    def display(self, droplet: dict) -> None:
        """Display droplet information."""
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
        """List available droplet templates."""
        try:
            templates = raw_droplet_templates()
            print(json.dumps(templates, indent=self.config.json_indent))
        except Exception as e:
            print(f"Error reading templates from: {e}")
    
    def _droplet_public_ip(self, droplet: dict) -> str:
        """Get the public IP address of a droplet."""
        for network in droplet.get('networks', {}).get('v4', []):
            if network.get('type') == 'public':
                return network.get('ip_address')
        return 'None'