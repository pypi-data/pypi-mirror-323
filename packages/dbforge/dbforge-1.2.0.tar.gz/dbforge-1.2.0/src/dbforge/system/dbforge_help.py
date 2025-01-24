"""Help text and documentation for DBForge commands"""
import click
from rich.console import Console
from rich.table import Table

class DBForgeHelp:
    """Help text and help command for DBForge"""
    
    def __init__(self):
        self.console = Console()
        
        # Help messages
        self.MAIN_HELP = "DBForge - A command-line tool for managing databases"
        self.COMMANDS_HELP = {
            "help": "Show this help message",
            "list": "List all configured databases",
            "create": "Create a new database configuration"
        }
        
        # Command options
        self.OPTIONS_HELP = {
            "type": "Database type (postgres, mysql, etc)"
        }
    
    def show_help(self):
        """Display help information"""
        table = Table(title="DBForge Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")
        
        # Add commands to help table
        for cmd, desc in self.COMMANDS_HELP.items():
            table.add_row(cmd, desc)
        
        # Print help
        self.console.print("\n" + self.MAIN_HELP + "\n")
        self.console.print(table)
        self.console.print("\nOptions:")
        for opt, desc in self.OPTIONS_HELP.items():
            self.console.print(f"  --{opt}: {desc}")
    
    def register_help(self, cli):
        """Register the help command with the CLI"""
        @cli.command()
        def help():
            """Show help information"""
            self.show_help()
