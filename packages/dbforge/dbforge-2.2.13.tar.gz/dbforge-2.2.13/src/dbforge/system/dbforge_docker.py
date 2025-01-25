"""Docker management functionality for DBForge"""
import platform
import os
import docker
from docker.errors import DockerException, ImageNotFound, APIError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
docker_client = None

def get_docker_client():
    """Get or create Docker client"""
    global docker_client
    if docker_client is None:
        try:
            docker_client = docker.from_env()
        except DockerException as e:
            console.print(f"[red]Failed to connect to Docker: {e}[/red]")
            return None
    return docker_client

def get_os():
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system

def is_root():
    return os.geteuid() == 0 if os.name == 'posix' else False

def check_docker_installed():
    """Check if Docker is installed and accessible"""
    client = get_docker_client()
    return client is not None

def check_docker_running():
    """Check if Docker daemon is running"""
    client = get_docker_client()
    if client:
        try:
            client.ping()
            return True
        except DockerException:
            return False
    return False

def get_docker_status():
    """Get Docker status information"""
    installed = check_docker_installed()
    running = installed and check_docker_running()
    
    status = {
        "installed": installed,
        "running": running
    }
    
    if installed and running:
        client = get_docker_client()
        try:
            version = client.version()["Version"]
            status["version"] = version
            
            containers = len(client.containers.list())
            status["active_containers"] = containers
        except DockerException:
            pass
    
    return status

def install_docker_macos():
    """Install Docker on macOS using Homebrew"""
    # Check if Homebrew is installed
    if not os.system("which brew > /dev/null") == 0:
        if Confirm.ask(
            "[yellow]Homebrew is required but not installed. Would you like to install it?[/yellow]"
        ):
            console.print("[yellow]Installing Homebrew...[/yellow]")
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            if os.system(install_cmd) != 0:
                console.print("[red]Failed to install Homebrew[/red]")
                return False
        else:
            console.print("[red]Homebrew is required for installation.[/red]")
            return False

    # Install Docker Desktop
    console.print("[yellow]Installing Docker Desktop...[/yellow]")
    if os.system("brew install --cask docker") != 0:
        console.print("[red]Failed to install Docker Desktop[/red]")
        return False
    
    console.print("[green]Docker Desktop installed successfully![/green]")
    console.print("Please start Docker Desktop from your Applications folder.")
    return True

def install_docker_linux():
    """Install Docker on Linux"""
    if not is_root():
        console.print("[red]This command requires root privileges. Please run with sudo.[/red]")
        return False

    # Use get.docker.com script for installation
    install_cmd = 'curl -fsSL https://get.docker.com | sh'
    if os.system(install_cmd) != 0:
        console.print("[red]Failed to install Docker[/red]")
        return False

    # Start and enable Docker service
    os.system("systemctl start docker")
    os.system("systemctl enable docker")

    # Add current user to docker group
    user = os.environ.get("SUDO_USER", os.environ.get("USER"))
    if user:
        os.system(f"usermod -aG docker {user}")
        console.print(f"[yellow]Added user {user} to docker group. Please log out and back in for changes to take effect.[/yellow]")

    return True

def show_docker_menu():
    """Show interactive Docker management menu"""
    table = Table(title="Docker Management", show_header=True, header_style="bold cyan")
    table.add_column("Option", style="cyan", justify="right")
    table.add_column("Description", style="green")
    
    options = {
        1: ("Check Status", "View Docker installation and running status"),
        2: ("Install Docker", "Install Docker on your system"),
        3: ("Clean Up", "Remove unused Docker resources"),
        4: ("Exit", "Return to main menu")
    }
    
    for num, (action, desc) in options.items():
        table.add_row(f"{num}", desc)
    
    while True:
        console.clear()
        console.print(table)
        
        try:
            choice = IntPrompt.ask("\nEnter your choice", choices=[str(i) for i in options.keys()])
            
            if choice == 1:
                show_status()
            elif choice == 2:
                install_docker_interactive()
            elif choice == 3:
                prune_docker()
            elif choice == 4:
                break
                
            if choice != 4:
                if Confirm.ask("\nReturn to Docker menu?"):
                    continue
                break
                
        except KeyboardInterrupt:
            break

def show_status():
    """Show Docker status"""
    status = get_docker_status()
    
    if not status["installed"]:
        console.print(Panel(
            "[red]Docker is not installed[/red]\n"
            "Select 'Install Docker' from the menu to install it automatically."
        ))
        return
    
    if not status["running"]:
        console.print(Panel("[yellow]Docker is installed but not running[/yellow]\n"
                          "Please start the Docker daemon"))
        return
    
    version = status.get("version", "Unknown")
    containers = status.get("active_containers", 0)
    
    console.print(Panel(
        f"[green]Docker Status:[/green]\n"
        f"• Version: {version}\n"
        f"• Running: Yes\n"
        f"• Active Containers: {containers}",
        title="Docker"
    ))

def install_docker_interactive():
    """Install Docker with interactive prompts"""
    if check_docker_installed():
        console.print("[yellow]Docker is already installed![/yellow]")
        if not check_docker_running():
            console.print("However, the Docker daemon is not running. Please start it.")
        return

    if not Confirm.ask("[yellow]Would you like to install Docker?[/yellow]"):
        return

    os_type = get_os()
    success = False

    if os_type == "macos":
        success = install_docker_macos()
    elif os_type == "linux":
        success = install_docker_linux()
    else:
        console.print(Panel(
            "[red]Automatic installation is not supported on your operating system.[/red]\n"
            "Please visit https://docs.docker.com/get-docker/ for manual installation instructions."
        ))
        return

    if success:
        console.print(Panel(
            "[green]Docker installation completed![/green]\n"
            "• For macOS: Open Docker Desktop from Applications\n"
            "• For Linux: Docker service should be running\n"
            "\nSelect 'Check Status' from the menu to verify the installation."
        ))
    else:
        console.print(Panel(
            "[red]Docker installation failed.[/red]\n"
            "Please try installing manually from: https://docs.docker.com/get-docker/"
        ))

def prune_docker():
    """Clean up unused Docker resources"""
    if not check_docker_installed() or not check_docker_running():
        console.print("[red]Docker is not available[/red]")
        return
    
    try:
        client = get_docker_client()
        client.containers.prune()
        client.images.prune()
        client.volumes.prune()
        client.networks.prune()
        console.print("[green]Cleanup complete![/green]")
    except DockerException as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")

def register_docker_commands(cli):
    """Register Docker-related commands with the CLI"""
    
    @cli.command()
    def docker():
        """Manage Docker integration"""
        show_docker_menu()

def check_docker():
    """Check if Docker is installed and running"""
    return check_docker_installed() and check_docker_running()

def ensure_docker():
    """Ensure Docker is installed and running"""
    if check_docker():
        return True
        
    console.print("\n[yellow]Docker is not installed or not running.[/yellow]")
    
    # Only offer installation on Ubuntu for now
    if platform.system() == "Linux" and "Ubuntu" in platform.version():
        if console.input("\nWould you like to install Docker? [y/n]: ").lower() == 'y':
            return install_docker_linux()
    else:
        console.print(Panel(
            "Please install Docker manually from:\n"
            "https://docs.docker.com/get-docker/",
            title="🐳 Docker Required",
            border_style="yellow"
        ))
    return False
