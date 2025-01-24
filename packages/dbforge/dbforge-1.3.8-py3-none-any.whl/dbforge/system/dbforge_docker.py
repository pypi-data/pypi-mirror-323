"""Docker management functionality for DBForge"""
import subprocess
import click
import platform
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

console = Console()

# Emoji constants for better readability
EMOJI_DOCKER = "🐳"
EMOJI_CHECK = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_ROCKET = "🚀"
EMOJI_GEAR = "⚙️"
EMOJI_BROOM = "🧹"
EMOJI_SPARKLES = "✨"
EMOJI_HOURGLASS = "⏳"

def get_os():
    """Get the current operating system"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system

def is_root():
    """Check if running with root/admin privileges"""
    return os.geteuid() == 0 if os.name == 'posix' else False

def create_fancy_spinner(message):
    """Create a fancy progress spinner with multiple columns"""
    return Progress(
        SpinnerColumn(spinner_name="dots12", style="cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        TimeRemainingColumn(),
        expand=True
    )

def run_with_spinner(message, command, shell=False):
    """Run a command with an enhanced spinner animation"""
    with create_fancy_spinner(message) as progress:
        task = progress.add_task(f"{EMOJI_GEAR} {message}", total=None)
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
    """Install Docker on macOS using Homebrew"""
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
    """Install Docker on Linux"""
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
    """Check if Docker is installed and running"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_docker_running():
    """Check if Docker daemon is running"""
    try:
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_docker_status():
    """Get detailed Docker status"""
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
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="menu"),
        Layout(name="footer")
    )

    header = Panel(
        Align.center(f"{EMOJI_DOCKER} Docker Management Console {EMOJI_DOCKER}", vertical="middle"),
        style="bold cyan",
        border_style="cyan"
    )
    
    table = Table(show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Option", style="cyan", justify="right")
    table.add_column("Action", style="green", justify="left")
    table.add_column("Description", style="blue")
    
    options = {
        1: ("Status", f"{EMOJI_GEAR} Check Docker Status", "View installation and running status"),
        2: ("Install", f"{EMOJI_ROCKET} Install Docker", "Set up Docker on your system"),
        3: ("Clean Up", f"{EMOJI_BROOM} Clean Resources", "Remove unused Docker resources"),
        4: ("Exit", "↩️ Exit", "Return to main menu")
    }
    
    for num, (action, emoji_action, desc) in options.items():
        table.add_row(f"[cyan]{num}[/cyan]", emoji_action, desc)
    
    footer = Panel(
        "[dim]Press Ctrl+C to exit at any time[/dim]",
        style="cyan"
    )
    
    layout["header"].update(header)
    layout["menu"].update(Align.center(table))
    layout["footer"].update(footer)

    while True:
        console.clear()
        console.print(layout)
        
        try:
            choice = IntPrompt.ask(
                f"\n{EMOJI_GEAR} Enter your choice",
                choices=[str(i) for i in options.keys()],
                show_choices=False
            )
            
            console.clear()
            if choice == 1:
                show_status()
            elif choice == 2:
                install_docker_interactive()
            elif choice == 3:
                prune_docker()
            elif choice == 4:
                console.print(f"\n{EMOJI_SPARKLES} Thanks for using Docker Management! {EMOJI_SPARKLES}")
                break
                
            if choice != 4:
                if Confirm.ask(f"\n{EMOJI_ROCKET} Return to Docker menu?"):
                    continue
                break
                
        except KeyboardInterrupt:
            console.print(f"\n{EMOJI_SPARKLES} Thanks for using Docker Management! {EMOJI_SPARKLES}")
            break

def show_status():
    """Show Docker status with animated display"""
    with create_fancy_spinner("Checking Docker status...") as progress:
        task = progress.add_task(f"{EMOJI_HOURGLASS} Checking Docker status...", total=100)
        
        # Animate the progress bar
        for i in range(100):
            time.sleep(0.01)
            progress.update(task, advance=1)
            
        status = get_docker_status()
    
    if not status["installed"]:
        console.print(Panel(
            f"{EMOJI_ERROR} [red]Docker is not installed[/red]\n\n"
            f"{EMOJI_ROCKET} Select 'Install Docker' from the menu to install it automatically.",
            title="Docker Status",
            border_style="red"
        ))
        return
    
    if not status["running"]:
        console.print(Panel(
            f"{EMOJI_WARNING} [yellow]Docker is installed but not running[/yellow]\n\n"
            f"{EMOJI_GEAR} Please start the Docker daemon",
            title="Docker Status",
            border_style="yellow"
        ))
        return
    
    version = status.get("version", "Unknown")
    containers = status.get("active_containers", 0)
    
    status_table = Table(show_header=False, border_style="green")
    status_table.add_column("Key", style="cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Version", version)
    status_table.add_row("Status", f"{EMOJI_CHECK} Running")
    status_table.add_row("Containers", f"{containers} active")
    
    console.print(Panel(
        status_table,
        title=f"{EMOJI_DOCKER} Docker Status {EMOJI_DOCKER}",
        border_style="green"
    ))

def install_docker_interactive():
    """Install Docker with interactive prompts and fancy display"""
    if check_docker_installed():
        console.print(f"\n{EMOJI_CHECK} [yellow]Docker is already installed![/yellow]")
        if not check_docker_running():
            console.print(f"{EMOJI_WARNING} However, the Docker daemon is not running. Please start it.")
        return

    if not Confirm.ask(f"\n{EMOJI_ROCKET} Would you like to install Docker?"):
        return

    os_type = get_os()
    success = False

    with Progress(
        SpinnerColumn(spinner_name="dots12"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="cyan"),
        TimeRemainingColumn(),
        expand=True
    ) as progress:
        task = progress.add_task(f"{EMOJI_GEAR} Preparing installation...", total=100)
        
        # Simulate preparation
        for i in range(50):
            time.sleep(0.02)
            progress.update(task, advance=1)
            
        if os_type == "macos":
            success = install_docker_macos()
        elif os_type == "linux":
            success = install_docker_linux()
        else:
            console.print(Panel(
                f"{EMOJI_ERROR} [red]Automatic installation is not supported on your operating system.[/red]\n\n"
                "Please visit https://docs.docker.com/get-docker/ for manual installation instructions.",
                border_style="red"
            ))
            return
            
        # Complete the progress
        progress.update(task, completed=100)

    if success:
        console.print(Panel(
            f"{EMOJI_CHECK} [green]Docker installation completed![/green]\n\n"
            f"{EMOJI_ROCKET} Next steps:\n"
            f"• For macOS: Open Docker Desktop from Applications\n"
            f"• For Linux: Docker service should be running\n\n"
            f"{EMOJI_GEAR} Select 'Check Status' from the menu to verify the installation.",
            title=f"{EMOJI_DOCKER} Installation Success {EMOJI_DOCKER}",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"{EMOJI_ERROR} [red]Docker installation failed.[/red]\n\n"
            "Please try installing manually from: https://docs.docker.com/get-docker/",
            border_style="red"
        ))

def prune_docker():
    """Clean up unused Docker resources with fancy animation"""
    if not check_docker_installed() or not check_docker_running():
        console.print(f"\n{EMOJI_ERROR} [red]Docker is not available[/red]")
        return
    
    try:
        with Progress(
            SpinnerColumn(spinner_name="dots12"),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="cyan"),
            TimeRemainingColumn(),
            expand=True
        ) as progress:
            task = progress.add_task(f"{EMOJI_BROOM} Cleaning up Docker resources...", total=100)
            
            # Start the cleanup
            process = subprocess.Popen(
                ["docker", "system", "prune", "-f"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Animate while waiting for completion
            while process.poll() is None:
                if progress.tasks[0].completed < 90:
                    progress.update(task, advance=5)
                time.sleep(0.1)
            
            # Complete the progress
            progress.update(task, completed=100)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                console.print(Panel(
                    f"{EMOJI_SPARKLES} [green]Cleanup complete![/green]\n\n"
                    f"Freed up resources:\n{stdout}",
                    title=f"{EMOJI_BROOM} Cleanup Success {EMOJI_BROOM}",
                    border_style="green"
                ))
            else:
                raise subprocess.CalledProcessError(process.returncode, "docker system prune", stderr)
                
    except subprocess.CalledProcessError as e:
        console.print(Panel(
            f"{EMOJI_ERROR} [red]Error during cleanup:[/red]\n{e}",
            border_style="red"
        ))

def register_docker_commands(cli):
    """Register Docker-related commands with the CLI"""
    
    @cli.command()
    def docker():
        """Manage Docker integration"""
        show_docker_menu()
