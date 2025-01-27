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

    def __init__(self):
        self.config = Config()
        self.client = DigitalOceanClient().get_client()
        self.action_manager = ActionManager()

    def create(self, template_name: str, volume_name: str, tags: tuple, dry_run: bool) -> None:
        """Create a volume."""
        try:
            req = volume_template(template_name, volume_name, tags)
            if dry_run:
                print(json.dumps(req, indent=self.config.json_indent))
            else:
                pass
                #resp = self.client.volumes.create(body=req)
                #if 'volume' in resp:
                #    self.display(resp['volume'])
                #else:
                #    self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error creating volume: {e}")

    def list(self):
        """List all volumes."""
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
        """Delete a volume."""
        try:
            assert volume_id not in self.config.protected_volumes, "Volume is protected."
            self.client.volumes.delete(volume_id)
        except Exception as e:
            print(f"Error deleting volume: {e}")

    def info(self, volume_id: str) -> None:
        """Get raw information about a volume."""
        try:
            resp = self.client.volumes.get(volume_id)
            if 'volume' in resp:
                print(json.dumps(resp['volume'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting volume info: {e}")
    
    def attach(self, volume_name: str, droplet_id: int) -> None:
        """Attach a volume to a droplet."""
        try:
            assert droplet_id not in self.config.protected_droplets, "Droplet is protected."
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
        """Detach a volume from a droplet."""
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
        """Display volume information."""
        print(
            f"ID: {volume['id']}, "
            f"Name: {volume['name']}, "
            f"Size: {volume['size_gigabytes']}, "
            f"Description: {volume['description']}, "
            f"DropletID: {self._volume_droplet_id(volume)}"
        )
    
    def templates(self) -> None:
        """List available volume templates."""
        try:
            templates = raw_volume_templates()
            print(json.dumps(templates, indent=self.config.json_indent))
        except Exception as e:
            print(f"Error reading templates from: {e}")
    
    def _volume_droplet_id(self, volume: dict) -> int:
        """Get the droplet id from a volume."""
        return volume['droplet_ids'][0] if volume['droplet_ids'] else 'None'