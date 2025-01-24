"""DBForge CLI implementation"""
import click
from rich.console import Console
from .system.dbforge_help import register_help

console = Console()

@click.group(add_help_option=False)
def cli():
    """dbforge - a command-line tool for managing databases"""
    pass

register_help(cli)
