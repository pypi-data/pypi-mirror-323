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
            Config._initialized = True
            self._read_config_file()
    
    def __getattr__(self, name):
        """Handles accessing environment variables and config file settings."""
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
        """Reads the config file from disk."""
        try:
            self._config = dict_from_file(basedir='.', filename=ProjectPaths.CONFIG_FILENAME)
        except FileNotFoundError:
            print(f"Missing file {ProjectPaths.CONFIG_FILENAME}.")
            print(f"Are you alreday created the project with `dom init`?")
            print(f"If so, are you working in the root dir of your project?")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)