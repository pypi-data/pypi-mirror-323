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

from digitalocean_manager.config import Config
from digitalocean_manager.project import ProjectPaths
from digitalocean_manager.reader import dict_from_file, read_file


config = Config()

def droplet_template(
    template_name: str,
    droplet_name: str,
    keys: tuple,
    volumes: tuple,
    tags: tuple,
    cloud_config: str
    ) -> dict:
    droplet = dict_from_file(ProjectPaths.DROPLETS_DIR, f'{template_name}.json')
    droplet['name'] = droplet_name
    droplet['region'] = config.digitalocean_region
    droplet['ssh_keys'] = list(keys) if keys else droplet.get('ssh_keys', [])
    droplet['volumes'] = list(volumes) if volumes else droplet.get('volumes', [])
    droplet['tags'] = list(tags) if tags else droplet.get('tags', [])
    droplet['user_data'] = cloud_config(cloud_config) if cloud_config else ''
    return droplet

def volume_template(template_name: str, volume_name: str, tags: tuple) -> dict:
    volume = dict_from_file(ProjectPaths.VOLUMES_DIR, f'{template_name}.json')
    volume['name'] = volume_name
    volume['region'] = config.digitalocean_region
    volume['tags'] = list(tags) if tags else volume.get('tags', [])
    return volume

def cloud_config(name: str) -> str:
    return read_file(ProjectPaths.CLOUD_CONFIGS_DIR, f"{name}.yaml")

def raw_json_templates(basedir: str) -> list:
    templates = []
    for filename in [f for f in os.listdir(basedir) if f.endswith('.json')]:
        name, _ = os.path.splitext(filename)
        content = dict_from_file(basedir, filename)
        templates.append({name: content})
    return templates

def raw_droplet_templates() -> list:
    return raw_json_templates(ProjectPaths.DROPLETS_DIR)

def raw_volume_templates() -> list:
    return raw_json_templates(ProjectPaths.VOLUMES_DIR)