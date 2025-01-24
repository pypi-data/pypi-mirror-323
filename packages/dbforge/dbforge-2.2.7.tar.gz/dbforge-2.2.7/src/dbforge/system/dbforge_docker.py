"""Docker management functionality for DBForge"""
import subprocess
import click
import platform
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def get_os():
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system

def is_root():
    return os.geteuid() == 0 if os.name == 'posix' else False

def run_with_spinner(message, command, shell=False):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=message, total=None)
        try:
            result = subprocess.run(
                command,
                shell=shell,
                check=True,
                capture_output=True,
                text=True
            )
            progress.update(task, completed=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            progress.update(task, completed=True)
            return False, e.stderr

def install_docker_macos():
    # Check if Homebrew is installed
    if not subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
        if Confirm.ask(
            "[yellow]Homebrew is required but not installed. Would you like to install it?[/yellow]"
        ):
            console.print("[yellow]Installing Homebrew...[/yellow]")
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            success, output = run_with_spinner(
                "Installing Homebrew...",
                install_cmd,
                shell=True
            )
            if not success:
                console.print(f"[red]Failed to install Homebrew: {output}[/red]")
                return False
        else:
            console.print("[red]Homebrew is required for installation.[/red]")
            return False

    # Install Docker Desktop
    console.print("[yellow]Installing Docker Desktop...[/yellow]")
    success, output = run_with_spinner(
        "Installing Docker Desktop...",
        ["brew", "install", "--cask", "docker"]
    )
    
    if not success:
        console.print(f"[red]Failed to install Docker Desktop: {output}[/red]")
        return False
    
    console.print("[green]Docker Desktop installed successfully![/green]")
    console.print("Please start Docker Desktop from your Applications folder.")
    return True

def install_docker_linux():
    if not is_root():
        console.print("[red]This command requires root privileges. Please run with sudo.[/red]")
        return False

    # Detect Linux distribution
    if os.path.exists("/etc/debian_version"):
        # Ubuntu/Debian
        commands = [
            ("Updating package list...", ["apt-get", "update"]),
            ("Installing prerequisites...", ["apt-get", "install", "-y", "apt-transport-https", "ca-certificates", "curl", "software-properties-common"]),
            ("Adding Docker GPG key...", ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "|", "apt-key", "add", "-"], True),
            ("Adding Docker repository...", ["add-apt-repository", "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"]),
            ("Installing Docker...", ["apt-get", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io"])
        ]
    elif os.path.exists("/etc/fedora-release"):
        # Fedora
        commands = [
            ("Installing prerequisites...", ["dnf", "-y", "install", "dnf-plugins-core"]),
            ("Adding Docker repository...", ["dnf", "config-manager", "--add-repo", "https://download.docker.com/linux/fedora/docker-ce.repo"]),
            ("Installing Docker...", ["dnf", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io"])
        ]
    else:
        console.print("[red]Unsupported Linux distribution[/red]")
        return False

    for message, command, *shell in commands:
        success, output = run_with_spinner(message, command, shell=bool(shell))
        if not success:
            console.print(f"[red]Failed: {output}[/red]")
            return False

    # Start and enable Docker service
    subprocess.run(["systemctl", "start", "docker"])
    subprocess.run(["systemctl", "enable", "docker"])

    # Add current user to docker group
    user = os.environ.get("SUDO_USER", os.environ.get("USER"))
    if user:
        subprocess.run(["usermod", "-aG", "docker", user])
        console.print(f"[yellow]Added user {user} to docker group. Please log out and back in for changes to take effect.[/yellow]")

    return True

def check_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_docker_running():
    try:
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_docker_status():
    installed = check_docker_installed()
    running = installed and check_docker_running()
    
    status = {
        "installed": installed,
        "running": running
    }
    
    if installed and running:
        try:
            # Get Docker version info
            version = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], 
                                  capture_output=True, text=True, check=True).stdout.strip()
            status["version"] = version
            
            # Get running containers count
            containers = subprocess.run(["docker", "ps", "-q"], 
                                     capture_output=True, text=True, check=True).stdout.strip().count('\n') + 1
            status["active_containers"] = containers if containers > 0 else 0
            
        except subprocess.CalledProcessError:
            pass
    
    return status

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
        console.print("[yellow]Cleaning up unused Docker resources...[/yellow]")
        subprocess.run(["docker", "system", "prune", "-f"], check=True)
        console.print("[green]Cleanup complete![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")

def register_docker_commands(cli):
    """Register Docker-related commands with the CLI"""
    
    @cli.command()
    def docker():
        """Manage Docker integration"""
        show_docker_menu()

def install_docker_ubuntu():
    """Install Docker on Ubuntu systems"""
    try:
        # Update package index and install prerequisites
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "gnupg"], check=True)
        
        # Add Docker's official GPG key
        subprocess.run(["sudo", "install", "-m", "0755", "-d", "/etc/apt/keyrings"], check=True)
        subprocess.run(["sudo", "curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "-o", "/etc/apt/keyrings/docker.asc"], check=True)
        subprocess.run(["sudo", "chmod", "a+r", "/etc/apt/keyrings/docker.asc"], check=True)

        # Add the repository to Apt sources
        repo_cmd = """echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"""
        subprocess.run(repo_cmd, shell=True, check=True)
        
        # Update package index again
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        
        # Install Docker packages
        subprocess.run([
            "sudo", "apt-get", "install", "-y",
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin"
        ], check=True)
        
        # Add current user to docker group
        current_user = os.environ.get("SUDO_USER", os.environ.get("USER"))
        subprocess.run(["sudo", "usermod", "-aG", "docker", current_user], check=True)
        
        console.print(Panel(
            "[green]Docker installed successfully![/green]\n\n"
            "• Docker Engine is now installed\n"
            "• Docker Compose is now installed\n"
            "• Current user added to docker group\n\n"
            "[yellow]Note: You may need to log out and back in for group changes to take effect.[/yellow]",
            title="🐳 Docker Installation Complete",
            border_style="green"
        ))
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(Panel(
            f"[red]Docker installation failed![/red]\n\n"
            f"Error: {str(e)}\n\n"
            "Please try installing manually from:\n"
            "https://docs.docker.com/engine/install/ubuntu/",
            title="❌ Installation Error",
            border_style="red"
        ))
        return False

def check_docker():
    """Check if Docker is installed and running"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def ensure_docker():
    """Ensure Docker is installed and running"""
    if check_docker():
        return True
        
    console.print("\n[yellow]Docker is not installed or not running.[/yellow]")
    
    # Only offer installation on Ubuntu for now
    if platform.system() == "Linux" and "Ubuntu" in platform.version():
        if console.input("\nWould you like to install Docker? [y/n]: ").lower() == 'y':
            return install_docker_ubuntu()
    else:
        console.print(Panel(
            "Please install Docker manually from:\n"
            "https://docs.docker.com/get-docker/",
            title="🐳 Docker Required",
            border_style="yellow"
        ))
    return False
