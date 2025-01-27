import os
from os.path import join
import requests
import platform
import getpass
import subprocess
import json

from rich.console import Console
from rich.table import Table
from rich import box
import click

from thunder.config import Config

BASEURL = "https://api.thundercompute.com:8443"
# For debug mode
if os.environ.get('API_DEBUG_MODE') == "1":
    BASEURL = 'http://localhost:8080'
    
PLATFORM = "unknown"
try:
    platform_str = platform.system().lower()
    if platform_str == "linux":
        PLATFORM = "linux"
    elif platform_str == "darwin":
        PLATFORM = "mac"
    elif platform_str == "windows":
        PLATFORM = "windows"
except Exception:
    pass

session = requests.Session()

def setup_instance(token):
    basedir = join(os.path.expanduser("~"), ".thunder")
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    scriptfile = join(basedir, "setup.sh")
    script_contents_file = join(os.path.dirname(__file__), "tnr_setup.sh")
    with open(script_contents_file, "r", encoding="utf-8") as f:
        setup_sh = f.read()

    if not os.path.exists(scriptfile):
        with open(scriptfile, "w+", encoding="utf-8") as f:
            f.write(setup_sh)
        os.chmod(scriptfile, 0o555)

        # Only add this if it doesn't exist inside the bashrc already
        bashrc = join(os.path.expanduser("~"), ".bashrc")
        if f". {scriptfile}" not in bashrc:
            with open(bashrc, "a", encoding="utf-8") as f:
                f.write(f"\nexport TNR_API_TOKEN={token}")
                f.write(f"\n# start tnr setup\n. {scriptfile}\n# end tnr setup\n")
    else:
        with open(scriptfile, "r", encoding="utf-8") as f:
            current_contents = f.read()

        if current_contents != setup_sh:
            os.chmod(scriptfile, 0o777)
            with open(scriptfile, "w+", encoding="utf-8") as f:
                f.write(setup_sh)
            os.chmod(scriptfile, 0o555)

def get_next_id(token):
    try:
        endpoint = f"{BASEURL}/next_id"
        response = session.get(
            endpoint, headers={"Authorization": f"Bearer {token}"}
        )
        return str(response.json()["id"]), None
    except Exception as e:
        return None, e
    
def remove_host_key(device_ip):
    try:
        subprocess.run(
            ['ssh-keygen', '-R', device_ip], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, 
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        return False

def enable_default_tnr_activate():
    with open(os.path.expanduser("~/.bashrc"), "r") as f:
        if "tnr activate" not in f.read():
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write("\ntnr activate\n")

def get_available_gpus():
    endpoint = f"{BASEURL}/hosts2"
    try:
        response = session.get(endpoint, timeout=10)
        if response.status_code != 200:
            return None

        return response.json()
    except Exception as e:
        return None


def save_token(filename, token):
    if os.path.isfile(filename):
        if platform.system() == "Windows":
            subprocess.run(
                ["icacls", rf"{filename}", "/grant", f"{getpass.getuser()}:R"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            os.chmod(filename, 0o600)

    with open(filename, "w") as f:
        f.write(token)

    if platform.system() == "Windows":
        subprocess.run(
            [
                "icacls",
                rf"{filename}",
                r"/inheritance:r",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["icacls", f"{filename}", "/grant:r", rf"{getpass.getuser()}:(R)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    else:
        os.chmod(filename, 0o400)


def delete_unused_keys():
    pass


def get_key_file(uuid):
    basedir = join(os.path.expanduser("~"), ".thunder")
    basedir = join(basedir, "keys")
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    return join(basedir, f"id_rsa_{uuid}")


def get_instances(token, use_cache=True):
    if use_cache and get_instances.cache is not None:
        return get_instances.cache

    endpoint = f"{BASEURL}/instances/list"
    try:
        response = session.get(
            endpoint, headers={"Authorization": f"Bearer {token}"}, timeout=30
        )
        if response.status_code != 200:
            return False, response.text, {}

        result = (True, None, response.json())
        if use_cache:
            get_instances.cache = result
        return result
    except Exception as e:
        return False, str(e), {}


get_instances.cache = None


def create_instance(token, cpu_cores, gpu_type, template):
    endpoint = f"{BASEURL}/instances/create/{cpu_cores}/{gpu_type}/{template}"
    try:
        response = session.post(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return False, response.text, None

        data = response.json()

        token_file = get_key_file(data["uuid"])
        save_token(token_file, data["key"])
        return True, None, data["identifier"]
    except Exception as e:
        return False, str(e), None


def delete_instance(instance_id, token):
    endpoint = f"{BASEURL}/instances/{instance_id}/delete"
    try:
        response = session.post(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return False, response.text

        return True, None
    except Exception as e:
        return False, str(e)


def start_instance(instance_id, token):
    endpoint = f"{BASEURL}/instances/{instance_id}/up"
    try:
        response = session.post(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return False, response.text

        return True, None
    except Exception as e:
        return False, str(e)


def stop_instance(instance_id, token):
    endpoint = f"{BASEURL}/instances/{instance_id}/down"
    try:
        response = session.post(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return False, response.text

        return True, None
    except Exception as e:
        return False, str(e)
    
def get_current_disk_size_ssh(ssh):
    """Retrieve the current disk size using SSH."""
    _, stdout, _ = ssh.exec_command("lsblk -b -o SIZE -n -d /dev/sda")
    size_bytes = stdout.read().strip()
    if not size_bytes:
        return None
    try:
        # Convert bytes to GB
        size_gb = int(size_bytes) / (1024 ** 3)
        return round(size_gb)
    except ValueError:
        return None


def resize_instance(instance_id, new_size, token):
    endpoint = f"{BASEURL}/instances/{instance_id}/resize"
    msg_dict = {
        'requested_size': new_size,
    }
    try:
        response = session.post(
            endpoint, 
            headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, 
            timeout=30,
            json=msg_dict
        )
        if response.status_code != 200:
            return False, response.text

        return True, None
    except Exception as e:
        return False, str(e)


def get_active_sessions(token):
    endpoint = f"{BASEURL}/active_sessions"
    try:
        response = session.get(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return None, []

        data = response.json()
        ip_address = data.get("ip", "N/A")
        sessions = data.get("sessions", [])
        return ip_address, sessions
    except Exception as e:
        return None, []



def add_key_to_instance(instance_id, token):
    endpoint = f"{BASEURL}/instances/{instance_id}/add_key"
    try:
        response = session.post(
            endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, timeout=30
        )
        if response.status_code != 200:
            return False, f"Failed to add key to instance {instance_id}: {response.text}"

        data = response.json()
        token_file = get_key_file(data["uuid"])
        save_token(token_file, data["key"])
        return True, None

    except Exception as e:
        return False, f"Error while adding key to instance {instance_id}: {str(e)}"
    
def get_ip(token):
    endpoint = f"{BASEURL}/current_ip"
    try:
        response = session.get(
            endpoint, 
            headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM}, 
            timeout=30,
        )
        if response.status_code != 200:
            return False, response.text

        return True, response.text
    except Exception as e:
        return False, str(e)


# Updating ~/.ssh/config automatically
SSH_DIR = os.path.join(os.path.expanduser("~"), ".ssh")
SSH_CONFIG_PATH = os.path.join(SSH_DIR, "config")
SSH_CONFIG_PERMISSIONS = 0o600
SSH_DIR_PERMISSIONS = 0o700

def ensure_ssh_dir():
    """Ensure SSH directory exists with correct permissions."""
    if not os.path.exists(SSH_DIR):
        os.makedirs(SSH_DIR, mode=SSH_DIR_PERMISSIONS)
    else:
        current_mode = os.stat(SSH_DIR).st_mode & 0o777
        if current_mode != SSH_DIR_PERMISSIONS:
            os.chmod(SSH_DIR, SSH_DIR_PERMISSIONS)

def read_ssh_config():
    """Read SSH config file with proper error handling and permissions."""
    try:
        ensure_ssh_dir()
        if not os.path.exists(SSH_CONFIG_PATH):
            return []

        # Check and fix file permissions
        current_mode = os.stat(SSH_CONFIG_PATH).st_mode & 0o777
        if current_mode != SSH_CONFIG_PERMISSIONS:
            os.chmod(SSH_CONFIG_PATH, SSH_CONFIG_PERMISSIONS)
            
        with open(SSH_CONFIG_PATH, "r", encoding="utf-8") as f:
            return f.readlines()
    except (IOError, OSError, UnicodeDecodeError) as e:
        return []

def clean_config_lines(lines):
    """Clean and normalize SSH config lines to ensure consistent formatting."""
    # Remove empty lines and normalize spacing
    cleaned = []
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("Host "):
            if cleaned and cleaned[-1] != "":  # Add single newline before Host entries
                cleaned.append("")
        cleaned.append(line)
    
    if cleaned:  # Ensure single newline at end of file
        cleaned.append("")
    return [line + "\n" for line in cleaned]

def write_ssh_config(lines):
    """Write SSH config with proper permissions and error handling."""
    try:
        ensure_ssh_dir()
        
        # Clean up the config lines
        lines = clean_config_lines(lines)
        
        # Write to temporary file first
        temp_path = os.path.join(SSH_DIR, "config.tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        # Set correct permissions before moving
        os.chmod(temp_path, SSH_CONFIG_PERMISSIONS)
        
        # Atomic replace
        os.replace(temp_path, SSH_CONFIG_PATH)
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

def add_instance_to_ssh_config(hostname, key_path, host_alias=None, port=None):
    """Add instance to SSH config with proper validation and formatting."""
    if not hostname or not key_path:
        raise ValueError("Hostname and key_path are required")
    
    config_lines = read_ssh_config()
    host_alias = host_alias or hostname

    # Remove any existing entry first
    config_lines = [line for line in config_lines if not (
        line.strip() == f"Host {host_alias}" or
        (line.startswith(" ") and any(prev.strip() == f"Host {host_alias}" 
            for prev in config_lines[:config_lines.index(line)]))
    )]

    new_entry = [
        f"Host {host_alias}\n",
        f"    HostName {hostname}\n",
        f"    User ubuntu\n",
        f"    IdentityFile {key_path}\n",
        f"    StrictHostKeyChecking no\n",
    ]
    
    if port:
        new_entry.append(f"    LocalForward {port} localhost:{port}\n")

    config_lines.extend(new_entry)
    write_ssh_config(config_lines)

def remove_instance_from_ssh_config(host_alias):
    """Remove instance from SSH config safely."""
    if not host_alias:
        return
        
    config_lines = read_ssh_config()
    new_lines = []
    skip_until_next_host = False
    
    for line in config_lines:
        if line.strip().startswith("Host "):
            skip_until_next_host = (line.strip() == f"Host {host_alias}")
        
        if not skip_until_next_host:
            new_lines.append(line)
            
    write_ssh_config(new_lines)

def get_ssh_config_entry(instance_name):
    """Get SSH config entry with proper validation and error handling."""
    if not instance_name:
        return False, None
        
    try:
        config_lines = read_ssh_config()
        entry_exists = False
        ip_address = None
        
        for i, line in enumerate(config_lines):
            if line.strip() == f"Host {instance_name}":
                entry_exists = True
                # Look ahead for HostName
                for next_line in config_lines[i+1:]:
                    if not next_line.startswith(" "):
                        break
                    if next_line.strip().startswith("HostName"):
                        ip_address = next_line.split()[1].strip()
                        break
                break
                
        return entry_exists, ip_address
    except Exception as e:
        return False, None

def update_ssh_config_ip(instance_name, new_ip_address, keyfile=None):
    """Update instance IP and optionally key file in SSH config atomically."""
    if not instance_name or not new_ip_address:
        return
        
    config_lines = read_ssh_config()
    new_lines = []
    in_target_host = False
    updated_ip = False
    has_strict_checking = False
    updated_key = False if keyfile else True  # If no keyfile, consider it updated
    
    for line in config_lines:
        stripped = line.strip()
        if stripped.startswith("Host "):
            if in_target_host:
                # Add any missing configurations before moving to next host
                if not has_strict_checking:
                    new_lines.append("    StrictHostKeyChecking no\n")
                if keyfile and not updated_key:
                    new_lines.append(f"    IdentityFile {keyfile}\n")
            in_target_host = (stripped == f"Host {instance_name}")
            has_strict_checking = False
            updated_key = False if keyfile else True
            new_lines.append(line)
            continue
            
        if in_target_host:
            if stripped.startswith("HostName") and not updated_ip:
                new_lines.append(f"    HostName {new_ip_address}\n")
                updated_ip = True
                continue
            if stripped.startswith("StrictHostKeyChecking"):
                has_strict_checking = True
            if keyfile and stripped.startswith("IdentityFile"):
                new_lines.append(f"    IdentityFile {keyfile}\n")
                updated_key = True
                continue
        
        new_lines.append(line)
    
    # Handle case where target host was last in file
    if in_target_host:
        if not has_strict_checking:
            new_lines.append("    StrictHostKeyChecking no\n")
        if keyfile and not updated_key:
            new_lines.append(f"    IdentityFile {keyfile}\n")
            
    if updated_ip:
        write_ssh_config(new_lines)

def validate_token(token):
    endpoint = f"https://api.thundercompute.com:8443/uid"
    response = session.get(endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM})
    
    if response.status_code == 200:
        return True, None
    elif response.status_code == 401:
        return False, "Invalid token, please update the TNR_API_TOKEN environment variable or login again"
    else:
        return False, "Failed to authenticate token, please use `tnr logout` and try again."


def display_available_gpus():
    available_gpus = get_available_gpus()
    if available_gpus is not None:
        console = Console()
        available_gpus_table = Table(
            title="🌐 Available GPUs:",
            title_style="bold cyan",
            title_justify="left",
            box=box.ROUNDED,
        )
        available_gpus_table.add_column(
            "GPU Type",
            justify="center",
        )
        available_gpus_table.add_column(
            "Node Size",
            justify="center",
        )

        for gpu_type, count in available_gpus.items():
            available_gpus_table.add_row(
                gpu_type,
                ", ".join(map(str, count)),
            )
        console.print(available_gpus_table)

def get_instance_id(token):
    success, ip_address = get_ip(token)
    if not success:
           instance_id = None
    if Config().getX("instanceId") == -1:
        success, error, instances = get_instances(token)
        if not success:
            click.echo(
                click.style(
                    f"Failed to list Thunder Compute instances: {error}",
                    fg="red",
                    bold=True,
                )
            )
            return -1

        for instance_id, metadata in instances.items():
            if "ip" in metadata and metadata["ip"] == ip_address:
                break
        else:
            instance_id = None

        Config().set("instanceId", instance_id)
        Config().save()
    else:
        instance_id = Config().getX("instanceId")
    return str(instance_id) if instance_id is not None else instance_id

def get_uid(token):
    endpoint = f"{BASEURL}/uid"
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {token}", "Platform": PLATFORM})

    if response.status_code != 200:
        raise click.ClickException(
            "Failed to get info about user, is the API token correct?"
        )
    return response.text
    