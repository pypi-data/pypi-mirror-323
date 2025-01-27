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
import sys

from digitalocean_manager.project import ProjectPaths
from digitalocean_manager.reader import dict_from_file


class Config:
    """
    Singleton class for managing configuration settings.

    This class follows the Singleton design pattern, ensuring only one instance
    of the Config class exists throughout the application. It handles reading configuration
    settings either from environment variables or a configuration file.

    Attributes:
        _instance (Config): The single instance of the Config class.
        _initialized (bool): Flag to ensure the configuration is only initialized once.
        _config (dict): The configuration settings loaded from the file.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Creates or returns the existing instance of the Config class.

        This ensures that only one instance of Config is ever created
        (Singleton pattern). If an instance already exists, it returns the
        existing one instead of creating a new one.

        Args:
            *args: Positional arguments for instance creation.
            **kwargs: Keyword arguments for instance creation.

        Returns:
            Config: The single instance of the Config class.
        """
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initializes the Config instance."""
        if not Config._initialized:
            self._read_config_file()
            Config._initialized = True
    
    def __getattr__(self, name):
        """
        Handles accessing environment variables and config file settings.

        If the requested attribute is uppercase, it checks for an environment
        variable with that name. If not found, it checks the loaded config file.

        Args:
            name (str): The name of the attribute being accessed.

        Returns:
            str: The value of the environment variable or config setting.

        Raises:
            ValueError: If the environment variable is not set.
            AttributeError: If the config setting is not found.
        """
        if name.isupper(): # From ENV Variables
            if os.getenv(name):
                return os.getenv(name)
            else:
                raise ValueError(f"Environment variable '{name}' is not set.")
        if name in self._config: # From config file
            return self._config[name]
        else:
            raise AttributeError(f"{self.__class__.__name__} attribute '{name}' is not set.")
    
    def _read_config_file(self) -> dict:
        """
        Reads the config file from disk.

        This method loads the configuration settings from the specified
        config file. If the file is missing or an error occurs, an error message
        is printed and the program exits.

        Raises:
            FileNotFoundError: If the config file is missing.
            Exception: For other errors while reading the config file.
        """
        try:
            self._config = dict_from_file(basedir='.', filename=ProjectPaths.CONFIG_FILENAME)
        except FileNotFoundError:
            print(f"Error: Missing {ProjectPaths.CONFIG_FILENAME} file.")
            print("Have you created the project using `dom init`?")
            print("If yes, make sure you're in the root directory of your project.")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)