"""Builder module for package-orchestrator.

This module packages the current repository into a Docker image and pushes it to a specified registry. It builds a wheel
if setup.py exists and uses run.py to execute sequential scripts.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from package_orchestrator.config import Config

def build_image(config: Config) -> str:
    """Builds a Docker image from the current repository and pushes it to the package registry.

    Args:
        config: Config object with registry and service details.

    Returns:
        str: The full image URI (e.g., 'ghcr.io/JENO87/package-orchestrator/my-service:latest').

    Raises:
        subprocess.CalledProcessError: If build or push fails.
        FileNotFoundError: If required files are missing.
        ValueError: If run.py is not found.
    """
    repo_dir = "."

    # Attempt to build a wheel if setup.py or pyproject.toml exists
    wheel_path = None
    if os.path.exists(f"{repo_dir}/setup.py") or os.path.exists(f"{repo_dir}/pyproject.toml"):
        print("Building Python wheel from setup.py or pyproject.toml...")
        subprocess.run([sys.executable, "-m", "build", "--outdir", "dist"], check=True)
        wheel_path = next(Path("dist").glob("*.whl"), None)
        if wheel_path:
            print(f"Wheel created at: {wheel_path}")
        else:
            print("No wheel file generated; using raw files.")

    # Generate Dockerfile
    print("Creating Dockerfile...")
    if not os.path.exists(f"{repo_dir}/run.py"):
        raise ValueError("run.py is required to execute the script sequence. Add it to your repo.")
    with open("Dockerfile", "w") as f:
        f.write("FROM python:3.9-slim\n")
        f.write("WORKDIR /app\n")
        if os.path.exists("requirements.txt"):
            f.write("COPY requirements.txt .\n")
            f.write("RUN pip install --no-cache-dir -r requirements.txt\n")
        if wheel_path:
            # Copy wheel to current directory to ensure it's in build context
            wheel_filename = os.path.basename(wheel_path)
            shutil.copy(wheel_path, wheel_filename)
            f.write(f"COPY {wheel_filename} .\n")
            f.write(f"RUN pip install {wheel_filename}\n")
        f.write("COPY run.py .\n")
        f.write("CMD [\"python\", \"run.py\"]\n")

    # Build and push Docker image
    image_uri = f"{config.package_registry_url}/{config.service_name}:latest"
    print(f"Building Docker image: {image_uri}")
    subprocess.run(["docker", "build", "-t", image_uri, "."], check=True)
    print(f"Pushing Docker image to {config.package_registry_url}...")
    subprocess.run(["docker", "push", image_uri], check=True)

    return image_uri