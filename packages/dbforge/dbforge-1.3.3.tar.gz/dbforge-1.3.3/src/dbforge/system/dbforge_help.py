"""Help text and documentation for DBForge commands"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import tomli
from pathlib import Path

console = Console()

def get_version():
    """Get version from pyproject.toml"""
    try:
        # Simply go up from src/dbforge/system to the root
        pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            return tomli.load(f)["project"]["version"]
    except:
        return "unknown"

def show_help():
    # Header
    header = Text()
    header.append("\dbforge - Database Management CLI", style="bold cyan")
    header.append(f" v{get_version()}\n", style="dim")
    header.append("A powerful command-line tool for managing and interacting with databases", style="italic")
    console.print(Panel(header, border_style="cyan"))

    # Commands table
    cmd_table = Table(title="Available Commands", show_header=True, box=None)
    cmd_table.add_column("Command", style="cyan", no_wrap=True)
    cmd_table.add_column("Description", style="green")
    
    commands = {
        "help": "Show this help message and command reference",
        "list": "List all configured database connections",
        "create": "Create a new database configuration",
        "connect": "Connect to a configured database",
        "backup": "Create a backup of a database",
        "restore": "Restore a database from backup",
        "migrate": "Run database migrations",
        "query": "Execute SQL queries directly"
    }
    
    for cmd, desc in commands.items():
        cmd_table.add_row(f"dbforge {cmd}", desc)
    
    console.print(cmd_table)
    
    # Options by category
    console.print("\n[bold]Options:[/bold]")
    
    options = {
        "Connection": {
            "type": "Database type (postgres, mysql, sqlite, etc)",
            "host": "Database host address",
            "port": "Port number for the connection",
            "user": "Username for authentication",
            "password": "Password for authentication (will prompt if not provided)"
        },
        "General": {
            "verbose": "Enable detailed output",
            "quiet": "Suppress all non-error output",
            "config": "Path to custom config file"
        }
    }
    
    for category, opts in options.items():
        opt_table = Table(title=category, show_header=False, box=None, padding=(0, 2))
        opt_table.add_column(style="yellow")
        opt_table.add_column(style="white")
        
        for opt, desc in opts.items():
            opt_table.add_row(f"--{opt}", desc)
        
        console.print(opt_table)
    
    # Footer
    console.print("\n[dim]For more information, visit: https://pypi.org/project/dbforge[/dim]\n")

def register_help(cli):
    """Register the help command with the CLI"""
    @cli.command()
    def help():
        """Show help information"""
        show_help()
