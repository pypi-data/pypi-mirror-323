"""DBForge CLI implementation"""
import click
from rich.console import Console
from rich.table import Table
from .system.dbforge_help import DBForgeHelp

console = Console()
help_system = DBForgeHelp()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    """DBForge - A command-line tool for managing databases"""
    if ctx.get_help():
        help_system.show_help()
        ctx.exit()

# Override the default help command
def help_cmd():
    """Show help information"""
    help_system.show_help()

cli.command(name='help')(help_cmd)

@cli.command()
def list():
    """List all configured database connections"""
    console.print("Listing database connections...")

@cli.command()
def create():
    """Create a new database configuration"""
    console.print("Creating new database configuration...")

@cli.command()
def connect():
    """Connect to a configured database"""
    console.print("Connecting to database...")

@cli.command()
def backup():
    """Create a backup of a database"""
    console.print("Creating database backup...")

@cli.command()
def restore():
    """Restore a database from backup"""
    console.print("Restoring database from backup...")

@cli.command()
def migrate():
    """Run database migrations"""
    console.print("Running database migrations...")

@cli.command()
def query():
    """Execute SQL queries directly"""
    console.print("Execute SQL query...") 