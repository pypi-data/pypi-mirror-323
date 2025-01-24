"""Help text and documentation for DBForge commands"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

class DBForgeHelp:
    """Help text and help command for DBForge"""
    
    def __init__(self):
        self.console = Console()
        
        # Help messages
        self.MAIN_HELP = {
            "title": "DBForge - Database Management CLI",
            "subtitle": "A powerful command-line tool for managing and interacting with databases",
            "version": "v1.0.0"
        }
        
        self.COMMANDS_HELP = {
            "help": "Show this help message and command reference",
            "list": "List all configured database connections",
            "create": "Create a new database configuration",
            "connect": "Connect to a configured database",
            "backup": "Create a backup of a database",
            "restore": "Restore a database from backup",
            "migrate": "Run database migrations",
            "query": "Execute SQL queries directly"
        }
        
        # Command options by category
        self.OPTIONS_HELP = {
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
    
    def show_help(self):
        """Display help information with rich formatting"""
        # Header
        header = Text()
        header.append(f"\n{self.MAIN_HELP['title']}", style="bold cyan")
        header.append(f" {self.MAIN_HELP['version']}\n", style="dim")
        header.append(self.MAIN_HELP['subtitle'], style="italic")
        self.console.print(Panel(header, border_style="cyan"))

        # Commands table
        cmd_table = Table(title="Available Commands", show_header=True, box=None)
        cmd_table.add_column("Command", style="cyan", no_wrap=True)
        cmd_table.add_column("Description", style="green")
        
        for cmd, desc in self.COMMANDS_HELP.items():
            cmd_table.add_row(f"dbforge {cmd}", desc)
        
        self.console.print(cmd_table)
        
        # Options by category
        self.console.print("\n[bold]Options:[/bold]")
        for category, options in self.OPTIONS_HELP.items():
            opt_table = Table(title=category, show_header=False, box=None, padding=(0, 2))
            opt_table.add_column(style="yellow")
            opt_table.add_column(style="white")
            
            for opt, desc in options.items():
                opt_table.add_row(f"--{opt}", desc)
            
            self.console.print(opt_table)
        
        # Footer
        self.console.print("\n[dim]For more information, visit: https://dbforge.docs.example.com[/dim]\n")
    
    def register_help(self, cli):
        """Register the help command with the CLI"""
        @cli.command()
        def help():
            """Show help information"""
            self.show_help()
