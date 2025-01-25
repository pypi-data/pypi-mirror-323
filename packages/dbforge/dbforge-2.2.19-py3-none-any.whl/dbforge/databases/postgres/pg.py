"""PostgreSQL database management functionality"""
from datetime import time
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
from ...system.dbforge_docker import ensure_docker, get_docker_client
from docker.errors import DockerException, NotFound
import json
import stat

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
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._container_name = "dbforge-postgres"
        self._config_file = Path.home() / ".dbforge" / "postgres" / "connections.json"
        
    def _save_connection_info(self):
        """Save connection info to secure file"""
        config_dir = self._config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Read existing connections
        connections = {}
        if self._config_file.exists():
            with open(self._config_file, 'r') as f:
                connections = json.load(f)
        
        # Update with current connection
        connections[self._container_name] = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password
        }
        
        # Write with secure permissions
        with open(self._config_file, 'w') as f:
            json.dump(connections, f, indent=2)
        # Set file permissions to only allow owner read/write
        os.chmod(self._config_file, stat.S_IRUSR | stat.S_IWUSR)
        
    def _load_connection_info(self) -> bool:
        """Load connection info from secure file"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r') as f:
                    connections = json.load(f)
                    if self._container_name in connections:
                        conn = connections[self._container_name]
                        self.host = conn["host"]
                        self.port = conn["port"]
                        self.user = conn["user"]
                        self.password = conn["password"]
                        return True
            return False
        except Exception:
            return False

    def _try_connection(self, test_host: str) -> bool:
        """Try connecting to a specific host"""
        try:
            # Try with provided password first
            if self.password:
                try:
                    conn = psycopg2.connect(
                        host=test_host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database="postgres",
                        connect_timeout=2
                    )
                    conn.close()
                    return True
                except:
                    pass

            # If no password or connection failed, try environment variable
            env_password = os.environ.get('POSTGRES_PASSWORD')
            if env_password:
                try:
                    conn = psycopg2.connect(
                        host=test_host,
                        port=self.port,
                        user=self.user,
                        password=env_password,
                        database="postgres",
                        connect_timeout=2
                    )
                    conn.close()
                    self.password = env_password
                    return True
                except:
                    pass

            return False
        except:
            return False

    def ensure_connection(self) -> None:
        """Ensure PostgreSQL connection, setup local if needed"""
        # First try to load saved connection info
        if self._load_connection_info():
            try:
                if self._try_connection(self.host):
                    return
            except Exception as e:
                console.print(f"[yellow]Warning: Could not connect with saved credentials: {e}[/yellow]")

        # Only proceed with Docker setup if we're explicitly trying localhost
        if self.host != "localhost" and self.host != "127.0.0.1":
            raise Exception(f"Could not connect to PostgreSQL at {self.host}:{self.port}")

        # Docker setup as last resort
        client = get_docker_client()
        if not client:
            raise Exception("Could not connect to PostgreSQL. Please ensure PostgreSQL is running and credentials are correct.")
        
        try:
            # Look for existing container first
            try:
                container = client.containers.get(self._container_name)
                if container.status == "running":
                    ports = container.ports
                    for container_port in ports:
                        if "5432/tcp" in container_port:
                            self.port = int(ports[container_port][0]["HostPort"])
                            if self._try_connection("localhost"):
                                self._save_connection_info()
                                return
            except NotFound:
                pass

            # If we get here, we need to set up a new container
            console.print("[yellow]Setting up local PostgreSQL with Docker...[/yellow]")
            success, password = self.setup_local_postgres()
            if success:
                self.password = password
                self.host = "localhost"
                self._save_connection_info()
                console.print(Panel(
                    f"[green]PostgreSQL setup complete![/green]\n\n"
                    f"[bold blue]Connection Details:[/bold blue]\n"
                    f"• Host: localhost\n"
                    f"• Port: {self.port}\n"
                    f"• User: {self.user}\n"
                    f"• Password: {self.password}",
                    title="🐘 PostgreSQL Ready",
                    border_style="green"
                ))
                return
                
        except DockerException as e:
            raise Exception(f"Docker error: {e}")

    def setup_local_postgres(self) -> Tuple[bool, str]:
        """Setup local PostgreSQL with Docker"""
        try:
            client = get_docker_client()
            if not client:
                raise Exception("Docker client not available")

            # Get public IP
            public_ip = get_server_ip()
            if public_ip == "0.0.0.0":
                raise Exception("Could not determine server IP address")
            self.host = public_ip

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
            
            # Check if container already exists and remove it
            try:
                container = client.containers.get(self._container_name)
                console.print("[yellow]Removing existing PostgreSQL container...[/yellow]")
                container.remove(force=True)
            except NotFound:
                pass
            
            # Create config directory and files
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
            
            # Pull latest postgres image
            console.print("[yellow]Pulling PostgreSQL image...[/yellow]")
            client.images.pull("postgres", tag="latest")
            
            # Start PostgreSQL container
            console.print(f"[yellow]Starting PostgreSQL on port {self.port}...[/yellow]")
            container = client.containers.run(
                "postgres:latest",
                name=self._container_name,
                detach=True,
                environment={
                    "POSTGRES_PASSWORD": password,
                    "POSTGRES_HOST_AUTH_METHOD": "scram-sha-256"
                },
                ports={'5432/tcp': self.port},
                volumes={
                    str(pg_config): {'bind': '/etc/postgresql/postgresql.conf', 'mode': 'ro'},
                    str(pg_hba): {'bind': '/etc/postgresql/pg_hba.conf', 'mode': 'ro'}
                },
                command=[
                    "-c", "config_file=/etc/postgresql/postgresql.conf",
                    "-c", "hba_file=/etc/postgresql/pg_hba.conf"
                ]
            )
            
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
                    import time
                    time.sleep(1)
            
            raise Exception("PostgreSQL container failed to start")
            
        except DockerException as e:
            raise Exception(f"Failed to setup local PostgreSQL: {e}")

        if success:
            # Save connection info after successful setup
            self._save_connection_info()
            
        return success, password

    def get_connection(self, database: str = "postgres") -> psycopg2.extensions.connection:
        """Get a PostgreSQL connection"""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=database,
            connect_timeout=3  # Fail fast if can't connect
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
        
        try:
            client = get_docker_client()
            if not client:
                raise Exception("Docker client not available")

            # Get the container
            container = client.containers.get(self._container_name)
            
            # Execute pg_dump inside the container
            exec_result = container.exec_run(
                [
                    "pg_dump",
                    "-h", "localhost",
                    "-p", "5432",
                    "-U", self.user,
                    "-F", "c",  # Custom format (compressed)
                    name
                ],
                environment={"PGPASSWORD": self.password}
            )
            
            if exec_result.exit_code != 0:
                raise Exception(f"Backup failed: {exec_result.output.decode()}")
            
            # Write the backup to file
            with open(backup_file, "wb") as f:
                f.write(exec_result.output)
            
            return str(backup_file)
            
        except DockerException as e:
            raise Exception(f"Backup failed: {e}")

    def restore_database(self, name: str, backup_file: str) -> bool:
        """Restore a PostgreSQL database from backup"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        try:
            client = get_docker_client()
            if not client:
                raise Exception("Docker client not available")

            # Get the container
            container = client.containers.get(self._container_name)
            
            # Create database if it doesn't exist
            try:
                self.create_database(name)
            except Exception:
                pass  # Database might already exist
            
            # Copy backup file into container
            with open(backup_file, "rb") as f:
                container.put_archive("/tmp", f.read())
            
            # Execute pg_restore inside the container
            exec_result = container.exec_run(
                [
                    "pg_restore",
                    "-h", "localhost",
                    "-p", "5432",
                    "-U", self.user,
                    "-d", name,
                    "-c",  # Clean (drop) database objects before recreating
                    "-F", "c",  # Custom format (compressed)
                    f"/tmp/{os.path.basename(backup_file)}"
                ],
                environment={"PGPASSWORD": self.password}
            )
            
            if exec_result.exit_code != 0:
                raise Exception(f"Restore failed: {exec_result.output.decode()}")
            
            # Clean up the temporary file
            container.exec_run(["rm", f"/tmp/{os.path.basename(backup_file)}"])
            
            return True
            
        except DockerException as e:
            raise Exception(f"Restore failed: {e}")

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

    def get_connection_string(self, database: str = "postgres") -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{database}"
