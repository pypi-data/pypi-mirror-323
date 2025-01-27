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

import pydo
from digitalocean_manager.config import Config


class DigitalOceanClient:
    """
    Client class for interacting with the DigitalOcean API.

    This class encapsulates the logic for interacting with the DigitalOcean API
    using the pydo client. It loads the configuration from the `Config` class and
    initializes the client with the provided API token.

    Attributes:
        config (Config): The configuration instance, providing access to settings.
        client (pydo.Client): The pydo client instance for interacting with the DigitalOcean API.
    """

    def __init__(self):
        """
        Initializes the DigitalOceanClient instance.

        This method retrieves the DigitalOcean API token from the configuration and
        creates an instance of the `pydo.Client` for interacting with the API.

        Raises:
            ValueError: If the DigitalOcean token is not available in the configuration.
        """
        self.config = Config()
        self.client = pydo.Client(token=self.config.DIGITALOCEAN_TOKEN)

    def get_client(self) -> pydo.Client:
        """
        Returns the pydo client instance.

        This method provides access to the initialized pydo client, allowing the user
        to interact with the DigitalOcean API.

        Returns:
            pydo.Client: The initialized pydo client instance.
        """
        return self.client
    
    def raise_api_error(self, resp: dict) -> None:
        """
        Raises an exception for an API error response.

        This method is invoked when the API returns an error response. It formats
        the response dictionary into a readable JSON string and raises an exception.

        Args:
            resp (dict): The error response dictionary returned by the API.

        Raises:
            Exception: A general exception with the formatted API error response.
        """
        raise Exception(f"API Error\n{json.dumps(resp, indent=self.config.json_indent)}")
