"""PostgreSQL CLI commands with simple and advanced usage"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from ..postgres.pg import PostgresManager
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Emoji constants for better UX
EMOJI_DB = "🗄️"
EMOJI_CHECK = "✅"
EMOJI_ERROR = "❌"
EMOJI_BACKUP = "💾"
EMOJI_RESTORE = "📥"
EMOJI_LIST = "📋"
EMOJI_INFO = "ℹ️"
EMOJI_WARNING = "⚠️"

def get_pg_manager(host, port, user, password) -> PostgresManager:
    """Get PostgreSQL manager instance"""
    pg = PostgresManager(
        host=host or 'localhost',
        port=port or 5432,
        user=user or 'postgres',
        password=password
    )
    # Ensure PostgreSQL is available
    pg.ensure_connection()
    return pg

def register_postgres_commands(cli):
    """Register PostgreSQL commands with the CLI"""
    
    # Common connection options
    connection_options = [
        click.option('--host', envvar='PG_HOST', help='PostgreSQL host'),
        click.option('--port', envvar='PG_PORT', type=int, help='PostgreSQL port'),
        click.option('--user', envvar='PG_USER', help='PostgreSQL user'),
        click.option('--password', envvar='PG_PASSWORD', help='PostgreSQL password'),
    ]

    def add_options(options):
        def _add_options(func):
            for option in reversed(options):
                func = option(func)
            return func
        return _add_options

    @cli.group()
    def postgres():
        """Manage PostgreSQL databases"""
        pass

    @postgres.command()
    @click.argument('name')
    @click.option('--owner', help="Database owner")
    @click.option('--encoding', default="UTF8", help="Database encoding")
    @click.option('--template', default="template1", help="Template database")
    @add_options(connection_options)
    def create(name, owner, encoding, template, host, port, user, password):
        """Create a new database"""
        try:
            pg = get_pg_manager(host, port, user, password)
            pg.create_database(name, owner, encoding, template)
            console.print(f"\n{EMOJI_CHECK} Database '{name}' created successfully!")
            
            # Show database info
            info = pg.get_database_info(name)
            console.print(Panel(
                f"• Name: {info['name']}\n"
                f"• Owner: {info['owner']}\n"
                f"• Size: {info['size']}\n"
                f"• Encoding: {info['encoding']}",
                title=f"{EMOJI_DB} Database Created",
                border_style="green"
            ))
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    @click.argument('name')
    @click.option('--force', is_flag=True, help="Force drop by terminating connections")
    @add_options(connection_options)
    def drop(name, force, host, port, user, password):
        """Drop a database"""
        if not Confirm.ask(f"\n{EMOJI_WARNING} Are you sure you want to drop '{name}'?"):
            return
            
        try:
            pg = get_pg_manager(host, port, user, password)
            pg.drop_database(name, force)
            console.print(f"\n{EMOJI_CHECK} Database dropped successfully!\n")
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    @add_options(connection_options)
    def list(host, port, user, password):
        """List all databases"""
        try:
            with Progress(
                SpinnerColumn(spinner_name="dots12", style="cyan"),
                TextColumn("[cyan]Fetching databases...", justify="right"),
                transient=True
            ) as progress:
                progress.add_task("fetch", total=None)
                pg = get_pg_manager(host, port, user, password)
                databases = pg.list_databases()
            
            table = Table(title=f"{EMOJI_LIST} PostgreSQL Databases")
            table.add_column("Name", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Owner", style="yellow")
            table.add_column("Encoding", style="blue")
            
            for db in databases:
                table.add_row(
                    db["name"],
                    db["size"],
                    db["owner"],
                    db["encoding"]
                )
            
            console.print("\n", table, "\n")
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    @click.argument('name')
    @click.option('--output-dir', default="backups", help="Backup output directory")
    @add_options(connection_options)
    def backup(name, output_dir, host, port, user, password):
        """Backup a database"""
        try:
            pg = get_pg_manager(host, port, user, password)
            backup_file = pg.backup_database(name, output_dir)
            console.print(Panel(
                f"{EMOJI_BACKUP} Backup created successfully!\n\n"
                f"Location: {backup_file}\n"
                f"Database: {name}",
                border_style="green"
            ))
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    @click.argument('name')
    @click.argument('backup_file')
    @add_options(connection_options)
    def restore(name, backup_file, host, port, user, password):
        """Restore a database from backup"""
        if not Confirm.ask(
            f"\n{EMOJI_WARNING} This will overwrite '{name}' if it exists. Continue?"
        ):
            return
            
        try:
            pg = get_pg_manager(host, port, user, password)
            pg.restore_database(name, backup_file)
            console.print(f"\n{EMOJI_RESTORE} Database restored successfully!\n")
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    @click.argument('name')
    @add_options(connection_options)
    def info(name, host, port, user, password):
        """Show detailed database information"""
        try:
            pg = get_pg_manager(host, port, user, password)
            info = pg.get_database_info(name)
            
            console.print(Panel(
                f"[bold]Basic Information[/bold]\n"
                f"• Name: {info['name']}\n"
                f"• Owner: {info['owner']}\n"
                f"• Size: {info['size']}\n"
                f"• Encoding: {info['encoding']}\n"
                f"• Collation: {info['collation']}\n"
                f"• Character Type: {info['ctype']}\n"
                f"• Tablespace: {info['tablespace']}\n\n"
                f"[bold]Statistics[/bold]\n"
                f"• Number of Tables: {info['tables']}\n"
                f"• Active Connections: {info['activity']}\n"
                f"• Installed Extensions: {', '.join(info['extensions'] or [])}",
                title=f"{EMOJI_INFO} Database Information",
                border_style="cyan"
            ))
        except Exception as e:
            console.print(f"\n{EMOJI_ERROR} Error: {e}\n")

    @postgres.command()
    def help():
        """Show PostgreSQL command help"""
        help_text = """
        # PostgreSQL Database Management

        ## Commands
        - `dbforge postgres create mydb` - Create a database
        - `dbforge postgres drop mydb` - Delete a database
        - `dbforge postgres list` - List all databases
        - `dbforge postgres backup mydb` - Backup a database
        - `dbforge postgres restore mydb backup.sql` - Restore from backup
        - `dbforge postgres info mydb` - Show database details

        ## Advanced Usage
        Add options for more control:
        ```bash
        # Create with custom settings
        dbforge postgres create mydb --owner admin --encoding UTF8

        # Force drop a database
        dbforge postgres drop mydb --force

        # Backup to custom directory
        dbforge postgres backup mydb --output-dir /path/to/backups
        ```

        ## Connection Options
        Add these to any command:
        - `--host` - Database host
        - `--port` - Port number
        - `--user` - Username
        - `--password` - Password

        ## Environment Variables
        Set these to avoid typing credentials:
        - `PG_HOST` - Database host
        - `PG_PORT` - Port number
        - `PG_USER` - Username
        - `PG_PASSWORD` - Password
        """
        console.print(Markdown(help_text))
