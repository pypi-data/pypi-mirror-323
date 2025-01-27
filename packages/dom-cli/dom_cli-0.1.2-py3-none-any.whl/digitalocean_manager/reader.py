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
import json

import yaml


def read_file(basedir: str, filename: str) -> str:
    """
    Reads a file from the specified directory and returns its content as plain text.

    Args:
        basedir (str): The base directory where the file is located.
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist in the specified directory.
        Exception: If an error occurs while reading the file.
    """
    try:
        filepath = os.path.join(os.getcwd(), basedir, filename)
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' does not exists.")
    except Exception as e:
        raise Exception(f"Error reading {basedir}/{filename}: {e}")


def dict_from_file(basedir: str, filename: str) -> dict:
    """
    Reads a JSON or YAML file from the specified directory and converts its content to a dictionary.

    Args:
        basedir (str): The base directory where the file is located.
        filename (str): The name of the file to read. Must end with '.json' or '.yaml'.

    Returns:
        dict: The content of the file as a dictionary.

    Raises:
        ValueError: If the file format is unsupported (not '.json' or '.yaml').
        FileNotFoundError: If the file does not exist in the specified directory.
        Exception: If an error occurs while reading or parsing the file.
    """
    if filename.endswith('json'):
        return json.loads(read_file(basedir, filename))
    elif filename.endswith('yaml'):
        return yaml.safe_load(read_file(basedir, filename))
    else:
        raise ValueError(f"Unsupported file format for '{filename}'")