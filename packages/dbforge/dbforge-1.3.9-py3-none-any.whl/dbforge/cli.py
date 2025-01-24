import click
from rich.console import Console
from .system.dbforge_help import register_help
from .system.dbforge_docker import register_docker_commands

console = Console()

@click.group(add_help_option=False)
def cli():
    """dbforge - a command-line tool for managing databases"""
    pass

register_help(cli)
register_docker_commands(cli)
