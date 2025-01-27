import os
import sys
import subprocess
from logging import getLogger
from pathlib import Path
from typer import Typer

logger = getLogger(__name__)
system = Typer(help="", no_args_is_help=True)


def ensure_root_privileges():
    """
    If not running as root, re-run this exact command with sudo.
    """
    if os.geteuid() != 0:
        logger.info("Elevating privileges: re-running with sudo...")
        command = ["sudo", sys.executable] + sys.argv
        subprocess.run(command)
        sys.exit(0)


@system.command("init")
def init():
    """
    Initialize the service. It will:
      1. Create or recreate a virtual environment in /opt/bruhh_venv
      2. Install dependencies
      3. Copy daemon code into the venv
      4. Create or recreate a systemd service for bruhh
      5. Enable & start the service
    """

    # (1) Ensure we have root/sudo
    ensure_root_privileges()

    # --- Paths ---
    # Root of this subcommands folder: src/bruhh/cli/subcommands/system.py
    # So we step out to find the daemon folder: src/bruhh/daemon
    # Adjust if your structure differs.
    base_path = Path(__file__).resolve().parent.parent.parent  # subcommands -> cli -> bruhh
    daemon_src = base_path / "daemon" / "main.py"
    requirements_path = (
        Path(__file__).resolve().parent.parent  # subcommands -> cli
        / "system"
        / "service-requirements.txt"
    )

    venv_path = Path("/opt/bruhh_venv")
    venv_python = venv_path / "bin" / "python"
    service_name = "bruhh.service"
    systemd_path = Path("/etc/systemd/system") / service_name

    # (2) Recreate or create the venv
    if venv_path.exists():
        logger.info(f"Virtual environment already exists at {venv_path}, removing it...")
        try:
            subprocess.run(["rm", "-rf", str(venv_path)], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove old virtual environment: {e}")
            sys.exit(1)

    logger.info(f"Creating venv at {venv_path} ...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        sys.exit(1)

    # (3) Install dependencies in the fresh venv
    if not requirements_path.is_file():
        logger.error(f"Requirements file not found: {requirements_path}")
        sys.exit(1)

    try:
        # Ensure pip is available and upgraded
        subprocess.run([str(venv_python), "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)

        # (Optional) install your local bruhh package instead of copying the daemon.
        # e.g. `pip install /path/to/bruhh/project`
        # subprocess.run([str(venv_python), "-m", "pip", "install", str(base_path)], check=True)

        # If you have a separate service-requirements.txt, install those:
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

    # (4) Copy the daemon code into the venv (only needed if not installing the package)
    daemon_target_dir = venv_path / "daemon"
    try:
        if not daemon_target_dir.exists():
            daemon_target_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", str(daemon_src), str(daemon_target_dir)], check=True)
        logger.info(f"Copied daemon code from {daemon_src} to {daemon_target_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to copy daemon files: {e}")
        sys.exit(1)

    # The final path we want to run:
    daemon_entry = daemon_target_dir / "main.py"

    # (5) Create or overwrite the systemd service file
    if systemd_path.exists():
        logger.info(f"Removing existing service file at {systemd_path} for recreation...")
        try:
            systemd_path.unlink()
        except Exception as e:
            logger.error(f"Failed to remove old service file: {e}")
            sys.exit(1)

    # ExecStart can either be: {venv_python} -m bruhh.daemon.main
    # or a direct path: {venv_python} /opt/bruhh_venv/daemon/main.py
    exec_start = f"{venv_python} {daemon_entry}"

    service_content = f"""\
[Unit]
Description=Bruhh background service
After=network.target

[Service]
Type=simple
ExecStart={exec_start}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

    logger.info(f"Writing systemd service file to {systemd_path} ...")
    try:
        with systemd_path.open("w") as f:
            f.write(service_content)
    except Exception as e:
        logger.error(f"Failed to write service file: {e}")
        sys.exit(1)

    # (6) Reload systemd, enable & start
    try:
        logger.info("Reloading systemd daemon ...")
        subprocess.run(["systemctl", "daemon-reload"], check=True)

        logger.info(f"Enabling {service_name} to start on boot ...")
        subprocess.run(["systemctl", "enable", service_name], check=True)

        logger.info(f"Starting {service_name} ...")
        subprocess.run(["systemctl", "start", service_name], check=True)
        logger.info(f"Service {service_name} has been started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to enable/start {service_name}: {e}")
        sys.exit(1)


@system.command("status")
def status():
    """
    Check the status of the background service.
    """
    service_name = "bruhh.service"
    logger.info(f"Checking status of {service_name}...")
    try:
        subprocess.run(["systemctl", "status", service_name], check=False)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check status of {service_name}: {e}")
        sys.exit(1)
