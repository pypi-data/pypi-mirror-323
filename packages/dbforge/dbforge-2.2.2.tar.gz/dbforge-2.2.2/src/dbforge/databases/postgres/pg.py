"""PostgreSQL database management functionality"""
from datetime import time
import subprocess
import os
import secrets
import string
import socket
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import psycopg2
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

def generate_secure_password(length: int = 25) -> str:
    """Generate a cryptographically secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure password has at least one of each: uppercase, lowercase, digit, special
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*" for c in password)):
            return password

def find_free_port(start_port: int = 5432, max_attempts: int = 100) -> int:
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found in range {start_port}-{start_port + max_attempts}")

def get_server_ip() -> str:
    """Get the server's public IP address"""
    def is_private_ip(ip: str) -> bool:
        """Check if an IP address is private"""
        ip_parts = [int(part) for part in ip.split('.')]
        return (
            ip_parts[0] == 10 or
            (ip_parts[0] == 172 and 16 <= ip_parts[1] <= 31) or
            (ip_parts[0] == 192 and ip_parts[1] == 168)
        )

    try:
        # First try to get the public IP from a public service
        import urllib.request
        import json
        
        try:
            with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=2) as response:
                public_ip = json.loads(response.read())['ip']
                return public_ip
        except Exception:
            pass  # Fall back to local IP detection
        
        # Try to get a non-private IP that can be used to connect from other machines
        addresses = []
        
        # Get all IPv4 addresses
        for iface in socket.getaddrinfo(socket.gethostname(), None):
            if iface[0] == socket.AF_INET:  # Only IPv4
                ip = iface[4][0]
                if not ip.startswith('127.'):  # Skip localhost
                    addresses.append((ip, is_private_ip(ip)))
        
        # Prefer public IPs over private ones
        public_ips = [ip for ip, is_private in addresses if not is_private]
        if public_ips:
            return public_ips[0]
            
        # If no public IPs, try getting the main interface IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
            
        # If we still have private IPs, use the first one
        private_ips = [ip for ip, is_private in addresses if is_private]
        if private_ips:
            return private_ips[0]
            
    except Exception as e:
        console.print(f"[yellow]Warning: Could not determine public IP: {e}[/yellow]")
        
    return '0.0.0.0'  # Last resort fallback

class PostgresManager:
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 user: str = "postgres", password: Optional[str] = None):
        self.host = host if host != "localhost" else get_server_ip()
        self.port = port
        self.user = user
        self.password = password
        self._container_name = "dbforge-postgres"
        
    def setup_local_postgres(self) -> Tuple[bool, str]:
        """Setup local PostgreSQL with Docker"""
        try:
            # Generate secure password for postgres user
            password = generate_secure_password()
            
            # Find an available port
            try:
                port = find_free_port(self.port)
                if port != self.port:
                    console.print(f"[yellow]Port {self.port} is in use, using port {port} instead[/yellow]")
                    self.port = port
            except RuntimeError as e:
                raise Exception(f"Port allocation failed: {e}")
            
            # Check if container already exists
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self._container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            
            if self._container_name in result.stdout:
                console.print("[yellow]Removing existing PostgreSQL container...[/yellow]")
                subprocess.run(["docker", "rm", "-f", self._container_name], check=True)
            
            # Pull the latest postgres image
            console.print("[yellow]Pulling PostgreSQL image...[/yellow]")
            subprocess.run(["docker", "pull", "postgres:latest"], check=True)
            
            # Create a custom postgresql.conf
            config_dir = Path.home() / ".dbforge" / "postgres"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            pg_config = config_dir / "postgresql.conf"
            with open(pg_config, "w") as f:
                f.write("""
# Connection settings
listen_addresses = '*'
max_connections = 100

# Memory settings
shared_buffers = 128MB
dynamic_shared_memory_type = posix

# Security
password_encryption = scram-sha-256
ssl = off

# Locale and encoding
datestyle = 'iso, mdy'
timezone = 'UTC'
lc_messages = 'en_US.utf8'
lc_monetary = 'en_US.utf8'
lc_numeric = 'en_US.utf8'
lc_time = 'en_US.utf8'

# Tuning
effective_cache_size = 512MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
                """.strip())
            
            # Create pg_hba.conf for authentication
            pg_hba = config_dir / "pg_hba.conf"
            with open(pg_hba, "w") as f:
                f.write("""
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             0.0.0.0/0              scram-sha-256
host    all            all             ::/0                    scram-sha-256
                """.strip())
            
            # Start PostgreSQL container with generated password and custom configs
            console.print(f"[yellow]Starting PostgreSQL on port {self.port}...[/yellow]")
            subprocess.run([
                "docker", "run", "-d",
                "--name", self._container_name,
                "-e", f"POSTGRES_PASSWORD={password}",
                "-e", "POSTGRES_HOST_AUTH_METHOD=scram-sha-256",
                "-v", f"{pg_config}:/etc/postgresql/postgresql.conf",
                "-v", f"{pg_hba}:/etc/postgresql/pg_hba.conf",
                "-p", f"{self.port}:5432",
                "postgres:latest",
                "-c", "config_file=/etc/postgresql/postgresql.conf",
                "-c", "hba_file=/etc/postgresql/pg_hba.conf"
            ], check=True)
            
            # Wait for PostgreSQL to be ready
            console.print("[yellow]Waiting for PostgreSQL to be ready...[/yellow]")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    # Try to connect
                    with psycopg2.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=password,
                        connect_timeout=1
                    ) as conn:
                        with conn.cursor() as cur:
                            # Create extension if needed
                            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
                            conn.commit()
                        return True, password
                except psycopg2.Error:
                    subprocess.run(["sleep", "1"], check=True)
            
            raise Exception("PostgreSQL container failed to start")
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to setup local PostgreSQL: {e}")
    
    def ensure_connection(self) -> None:
        """Ensure PostgreSQL connection, setup local if needed"""
        try:
            self._test_connection()
        except Exception as e:
            console.print(f"\n[yellow]PostgreSQL not available: {e}[/yellow]")
            console.print("[yellow]Setting up local PostgreSQL with Docker...[/yellow]")
            success, password = self.setup_local_postgres()
            if success:
                self.password = password
                console.print(Panel(
                    f"[green]PostgreSQL setup complete![/green]\n\n"
                    f"[bold blue]Connection Details (Works from any machine):[/bold blue]\n"
                    f"• Host: {self.host} (Server IP)\n"
                    f"• Port: {self.port}\n"
                    f"• User: {self.user}\n"
                    f"• Password: {self.password}\n\n"
                    f"[yellow]Example connection string:[/yellow]\n"
                    f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/postgres\n\n"
                    "[yellow]Save these credentials securely![/yellow]",
                    title="🐘 PostgreSQL Ready",
                    border_style="green"
                ))
            else:
                raise Exception("Failed to setup local PostgreSQL")

    def _test_connection(self) -> bool:
        """Test the PostgreSQL connection"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    def get_connection(self, database: str = "postgres") -> psycopg2.extensions.connection:
        """Get a PostgreSQL connection"""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=database
        )

    def list_databases(self) -> List[Dict]:
        """List all databases with their sizes and stats"""
        query = """
        SELECT d.datname as name,
               pg_size_pretty(pg_database_size(d.datname)) as size,
               t.spcname as tablespace,
               u.usename as owner,
               pg_encoding_to_char(d.encoding) as encoding
        FROM pg_database d
        JOIN pg_tablespace t ON d.dattablespace = t.oid
        JOIN pg_user u ON d.datdba = u.usesysid
        WHERE d.datistemplate = false
        ORDER BY pg_database_size(d.datname) DESC;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                return [
                    {
                        "name": row[0],
                        "size": row[1],
                        "tablespace": row[2],
                        "owner": row[3],
                        "encoding": row[4]
                    }
                    for row in results
                ]

    def create_database(self, name: str, owner: Optional[str] = None, 
                       encoding: str = "UTF8", template: str = "template1") -> bool:
        """Create a new PostgreSQL database"""
        # We need to connect with autocommit because CREATE DATABASE cannot run inside a transaction
        conn = self.get_connection()
        conn.autocommit = True  # Set autocommit before doing anything
        try:
            with conn.cursor() as cur:
                # Escape the database name
                safe_name = psycopg2.extensions.quote_ident(name, conn)
                
                # Build the CREATE DATABASE command
                create_cmd = f"CREATE DATABASE {safe_name}"
                if owner:
                    create_cmd += f" OWNER = {psycopg2.extensions.quote_ident(owner, conn)}"
                create_cmd += f" ENCODING = '{encoding}'"
                create_cmd += f" TEMPLATE = {psycopg2.extensions.quote_ident(template, conn)}"
                
                try:
                    cur.execute(create_cmd)
                    return True
                except Exception as e:
                    raise Exception(f"Failed to create database: {e}")
        finally:
            conn.close()

    def drop_database(self, name: str, force: bool = False) -> bool:
        """Drop a PostgreSQL database"""
        with self.get_connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                safe_name = psycopg2.extensions.quote_ident(name, conn)
                
                if force:
                    # Terminate all connections to the database
                    cur.execute(f"""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s AND pid != pg_backend_pid()
                    """, (name,))
                
                try:
                    cur.execute(f"DROP DATABASE {safe_name}")
                    return True
                except Exception as e:
                    raise Exception(f"Failed to drop database: {e}")

    def backup_database(self, name: str, output_dir: str = "backups") -> str:
        """Backup a PostgreSQL database"""
        # Ensure backup directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        backup_file = Path(output_dir) / f"{name}_{int(time.time())}.sql"
        
        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h", self.host,
            "-p", str(self.port),
            "-U", self.user,
            "-F", "c",  # Custom format (compressed)
            "-f", str(backup_file),
            name
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            return str(backup_file)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Backup failed: {e.stderr.decode()}")

    def restore_database(self, name: str, backup_file: str) -> bool:
        """Restore a PostgreSQL database from backup"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Create database if it doesn't exist
        try:
            self.create_database(name)
        except Exception:
            pass  # Database might already exist
        
        # Build pg_restore command
        cmd = [
            "pg_restore",
            "-h", self.host,
            "-p", str(self.port),
            "-U", self.user,
            "-d", name,
            "-c",  # Clean (drop) database objects before recreating
            "-F", "c",  # Custom format (compressed)
            backup_file
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore failed: {e.stderr.decode()}")

    def get_database_info(self, name: str) -> Dict:
        """Get detailed information about a database"""
        queries = {
            "size": "SELECT pg_size_pretty(pg_database_size(%s))",
            "tables": """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """,
            "extensions": "SELECT array_agg(extname) FROM pg_extension",
            "activity": """
                SELECT COUNT(*) 
                FROM pg_stat_activity 
                WHERE datname = %s
            """
        }
        
        info = {}
        with self.get_connection(name) as conn:
            with conn.cursor() as cur:
                # Get basic info
                cur.execute("""
                    SELECT 
                        d.datname as name,
                        u.usename as owner,
                        pg_encoding_to_char(d.encoding) as encoding,
                        d.datcollate as collation,
                        d.datctype as ctype,
                        pg_size_pretty(pg_database_size(d.datname)) as size,
                        t.spcname as tablespace
                    FROM pg_database d
                    JOIN pg_user u ON d.datdba = u.usesysid
                    JOIN pg_tablespace t ON d.dattablespace = t.oid
                    WHERE d.datname = %s
                """, (name,))
                result = cur.fetchone()
                if result:
                    info.update({
                        "name": result[0],
                        "owner": result[1],
                        "encoding": result[2],
                        "collation": result[3],
                        "ctype": result[4],
                        "size": result[5],
                        "tablespace": result[6]
                    })
                
                # Get additional stats
                for key, query in queries.items():
                    cur.execute(query, (name,))
                    info[key] = cur.fetchone()[0]
        
        return info
