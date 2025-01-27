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
    """
    A class to manage and track actions in DigitalOcean.

    Attributes:
        config (Config): Configuration object to handle settings and configurations.
        client (Client): DigitalOcean API client instance.
    """

    def __init__(self):
        """
        Initialize the ActionManager with configuration and client.

        Sets up the necessary client and configuration for managing actions.
        """
        self.config = Config()
        self.client = DigitalOceanClient().get_client()

    def info(self, action_id: int) -> str:
        """
        Get raw information about an action.

        Args:
            action_id (int): The ID of the action to retrieve information for.

        Returns:
            str: A JSON-formatted string containing information about the action.

        Raises:
            Exception: If there is an error retrieving the action info.

        This method retrieves and prints detailed information about a specific action
        using the provided action ID. The result is displayed in a formatted JSON string.
        """
        try:
            resp = self.client.actions.get(action_id)
            if 'action' in resp:
                print(json.dumps(resp['action'], indent=self.config.json_indent))
            else:
                self.client.raise_api_error(resp)
        except Exception as e:
            print(f"Error getting action info: {e}")
    
    def ping(self, action_id: int) -> str:
        """
        Ping the status of an action until it is completed.

        Args:
            action_id (int): The ID of the action to ping.

        Raises:
            Exception: If there is an error checking the action status.

        This method continuously checks the status of the specified action at regular intervals
        until the action is either completed or errored out. It prints the action details each time.
        """
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
        """
        Display information about an action.

        Args:
            action (dict): The action object containing details about the action.

        This method prints key information about the action, including its ID, status,
        type, and timestamps for when it started and completed.
        """
        print(
            f"ActionID: {action['id']}, "
            f"Status: {action['status']}, "
            f"Type: {action['type']}, "
            f"StartedAt: {action['started_at']}, "
            f"CompletedAt: {action['completed_at']}"
        )