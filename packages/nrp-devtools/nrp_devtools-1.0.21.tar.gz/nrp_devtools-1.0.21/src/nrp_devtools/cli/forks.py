from typing import Any

import click

from ..commands.forks import apply_forks
from ..commands.resolver import get_resolver
from ..config import OARepoConfig
from .base import command_sequence, nrp_command


@nrp_command.group(name="forks")
def forks_group(**kwargs: Any):
    pass


@forks_group.command(name="add", help="Add a fork")
@click.argument("python_package")
@click.argument("git_fork_url")
@command_sequence(save=True)
def add_fork_command(
    *, config: OARepoConfig, python_package: str, git_fork_url: str, **kwargs: Any
):
    config.add_fork(python_package, git_fork_url)


@forks_group.command(name="remove", help="Remove a fork")
@click.argument("python_package")
@command_sequence(save=True)
def remove_fork_command(*, config: OARepoConfig, python_package: str, **kwargs: Any):
    config.remove_fork(python_package)


@forks_group.command(name="list", help="List all forks")
@command_sequence()
def list_forks_command(*, config: OARepoConfig, **kwargs: Any):
    for package, url in config.forks.items():
        click.echo(f"{package}: {url}")


@forks_group.command(name="apply", help="Apply all forks")
@command_sequence()
def apply_forks_command(*, config: OARepoConfig, **kwargs: Any):
    resolver = get_resolver(config)
    apply_forks(config, resolver)
