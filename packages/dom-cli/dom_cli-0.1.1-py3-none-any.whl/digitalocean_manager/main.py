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

import click


@click.group()
def cli():
    """DigitalOcean Manager CLI."""
    pass


@cli.command()
def init():
    """Create a new project in the current directory."""
    from digitalocean_manager.project import Project
    Project().create()


"""
Droplet subcommands

The `droplet` command group has the following subcommands:
- create: Create a new droplet.
- stop: Stop an existing droplet.
- start: Start an existing droplet.
- delete: Delete an existing droplet.
- list: List all droplets.
- info: Get information about a droplet.
- templates: List all droplet templates.
"""
@cli.group()
def droplet():
    """Manage droplets."""
    pass


@droplet.command()
@click.argument("template_name")
@click.argument("droplet_name")
@click.option("-k", "--key", "keys", multiple=True, help="SSH key ID to attach to the droplet.")
@click.option("-v", "--volume-id", "volumes", multiple=True, help="Volume ID to attach to the droplet.")
@click.option("-t", "--tag", "tags", multiple=True, help="Tag to attach to the droplet.")
@click.option("-c", "--cloud-config", "cloud_config", help="Cloud config filename to attach to the droplet.")
@click.option("--dry-run", default=False, is_flag=True, help="Shows the data will send to DigitalOcean without perform any request.")
def create(
    template_name: str,
    droplet_name: str,
    keys: tuple,
    volumes: tuple,
    tags: tuple,
    cloud_config: str,
    dry_run: bool,
):
    """Create a new droplet."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().create(template_name, droplet_name, keys, volumes, tags, cloud_config, dry_run)


@droplet.command()
@click.argument("droplet_id", type=int)
def stop(droplet_id: int):
    """Stop an existing droplet."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().stop(droplet_id)


@droplet.command()
@click.argument("droplet_id", type=int)
def start(droplet_id: int):
    """Start an existing droplet."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().start(droplet_id)


@droplet.command()
@click.argument("droplet_id", type=int)
def delete(droplet_id: int):
    """Delete an existing droplet."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().delete(droplet_id)


@droplet.command()
@click.option("-t", "--droplet-type", default='cpu', help="Type of droplets to list ['cpu','gpu'].")
def list(droplet_type: str):
    """List all droplets."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().list(droplet_type)


@droplet.command()
@click.argument("droplet_id", type=int)
def info(droplet_id: int):
    """Get information about a droplet."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().info(droplet_id)


@droplet.command()
def templates():
    """List all droplet templates."""
    from digitalocean_manager.managers.droplet import DropletManager
    DropletManager().templates()


"""
Volume subcommands

The `volume` command group has the following subcommands:
- create: Create a new volume.
- attach: Attach a volume to a droplet.
- detach: Detach a volume from a droplet.
- delete: Delete a volume.
- list: List all volumes.
- info: Get information about a volume.
- templates: List all volume templates.
"""
@cli.group()
def volume():
    """Manage volumes."""
    pass


@volume.command()
@click.argument("template_name")
@click.argument("volume_name")
@click.option("-t", "--tag", "tags", multiple=True, help="Tag to attach to the droplet.")
@click.option("--dry-run", default=False, is_flag=True, help="Shows the data will send to DigitalOcean without perform any request.")
def create(template_name: str, volume_name: str, tags: tuple, dry_run: bool):
    """Create a new volume."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().create(template_name, volume_name, tags, dry_run)


@volume.command()
@click.argument("volume_name")
@click.argument("droplet_id")
def attach(volume_name: str, droplet_id: int):
    """Attach a volume to a droplet."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().attach(volume_name, droplet_id)


@volume.command()
@click.argument("volume_name")
@click.argument("droplet_id")
def detach(volume_name: str, droplet_id: int):
    """Detach a volume from a droplet."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().detach(volume_name, droplet_id)


@volume.command()
@click.argument("volume_id")
def delete(volume_id: str):
    """Delete a volume by id."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().delete(volume_id)


@volume.command()
def list():
    """List all volumes."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().list()


@volume.command()
@click.argument("volume_id")
def info(volume_id: str):
    """Get information about a volume."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().info(volume_id)


@volume.command()
def templates():
    """List all volume templates."""
    from digitalocean_manager.managers.volume import VolumeManager
    VolumeManager().templates()


"""
SSH key subcommands

The `sshkey` command group has the following subcommands:
- list: List all SSH keys.
- info: Get information about an SSH key.
"""
# SSH key subcommands
@cli.group()
def key():
    """Manage SSH keys."""
    pass


@key.command()
def list():
    """List all SSH keys."""
    from digitalocean_manager.managers.sshkey import SSHKeyManager
    SSHKeyManager().list()


@key.command()
@click.argument("ssh_key_id", type=int)
def info(ssh_key_id: int):
    """Get information about an SSH key."""
    from digitalocean_manager.managers.sshkey import SSHKeyManager
    SSHKeyManager().info(ssh_key_id)


"""
Action subcommands

The `action` command group has the following subcommands:
- info: Get information about an action.
"""
@cli.group()
def action():
    """Manage actions."""
    pass


@action.command()
@click.argument("action_id")
def info(action_id):
    """Get information about an action_id."""
    from digitalocean_manager.managers.action import ActionManager
    ActionManager().info(action_id)


"""
Program version
"""
@cli.command()
def version():
    """Show the version of the tool."""
    from digitalocean_manager.__version__ import __version__
    click.echo(f"DigitalOcean Manager {__version__}")


if __name__ == "__main__":
    cli()