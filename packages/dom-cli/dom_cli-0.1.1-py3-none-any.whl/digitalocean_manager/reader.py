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
    """Read file and returns plain text."""
    try:
        filepath = os.path.join(os.getcwd(), basedir, filename)
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' does not exists.")
    except Exception as e:
        raise Exception(f"Error reading {basedir}/{filename}: {e}")


def dict_from_file(basedir: str, filename: str) -> dict:
    """Read the config json/yaml file and converts it to dict."""
    if filename.endswith('json'):
        return json.loads(read_file(basedir, filename))
    elif filename.endswith('yaml'):
        return yaml.safe_load(read_file(basedir, filename))
    else:
        raise ValueError(f"Unsupported file format for '{filename}'")