"""DBForge CLI implementation"""
import click
from rich.console import Console
from rich.table import Table
from .system.dbforge_help import DBForgeHelp

console = Console()
help_system = DBForgeHelp()

@click.group()
def cli():
    """DBForge - A command-line tool for managing databases"""
    pass


# Register help command
help_system.register_help(cli) 