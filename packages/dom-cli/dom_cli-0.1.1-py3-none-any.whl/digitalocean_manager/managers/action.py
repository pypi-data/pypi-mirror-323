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
import time

from digitalocean_manager.config import Config
from digitalocean_manager.client import DigitalOceanClient


class ActionManager:

    def __init__(self):
        self.config = Config()
        self.client = DigitalOceanClient().get_client()

    def info(self, action_id: int) -> str:
        """Get raw information about an action."""
        try:
            resp = self.client.actions.get(action_id)
            if 'action' in resp:
                print(json.dumps(resp['action'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting action info: {e}")
    
    def ping(self, action_id: int) -> str:
        """Ping the status of an action until it is completed."""
        while True:
            time.sleep(self.config.ping_interval)
            resp = self.client.actions.get(action_id)
            if 'action' in resp:
                self.display(resp['action'])
                if resp['action']['status'] in ('completed', 'errored'):
                    break
            else:
                self.client.raise_api_error(resp)
                break
        
    def display(self, action: dict) -> None:
        """Display action information."""
        print(
            f"ActionID: {action['id']}, "
            f"Status: {action['status']}, "
            f"Type: {action['type']}, "
            f"StartedAt: {action['started_at']}, "
            f"CompletedAt: {action['completed_at']}"
        )