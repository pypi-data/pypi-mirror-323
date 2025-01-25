import click
from rich.console import Console
from rich.table import Table
from .system.dbforge_help import register_help
from .system.dbforge_docker import register_docker_commands, get_docker_client
from .databases.commands.pg_cmds import register_postgres_commands

console = Console()

@click.group(add_help_option=False)
def cli():
    """dbforge - a command-line tool for managing databases"""
    pass

@cli.command()
def list():
    """List all running database containers"""
    client = get_docker_client()
    if not client:
        console.print("[red]Error: Docker is not running or not accessible[/red]")
        return

    try:
        containers = client.containers.list(filters={"status": "running"})
        
        table = Table(title="🗄️ Running Database Containers")
        table.add_column("Name", style="cyan")
        table.add_column("Image", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Ports", style="blue")
        
        for container in containers:
            # Get port mappings
            ports = []
            for container_port, host_config in container.ports.items():
                if host_config:
                    for config in host_config:
                        ports.append(f"{config['HostPort']}->{container_port}")
            ports_str = ", ".join(ports) if ports else "No ports exposed"
            
            table.add_row(
                container.name,
                container.image.tags[0] if container.image.tags else "No tag",
                container.status,
                ports_str
            )
        
        if containers:
            console.print("\n", table, "\n")
        else:
            console.print("\n[yellow]No running database containers found[/yellow]\n")
            
    except Exception as e:
        console.print(f"[red]Error listing containers: {e}[/red]")

register_help(cli)
register_docker_commands(cli)
register_postgres_commands(cli)
