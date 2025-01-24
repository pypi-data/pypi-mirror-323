"""PostgreSQL database management functionality"""
from datetime import time
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, List
import psycopg2
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class PostgresManager:
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 user: str = "postgres", password: Optional[str] = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._test_connection()

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
        with self.get_connection() as conn:
            conn.autocommit = True
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
