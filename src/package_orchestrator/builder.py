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
from loguru import logger
import importlib.metadata

def build_image(config: Config) -> str:
    """Builds a Docker image from the current repository and pushes it to the package registry.
    Args:
        config: Config object with registry and service details.
    Returns:
        str: The full image URI (e.g., 'ghcr.io/JENO87/package-orchestrator/my-service:1.0.0').
    Raises:
        subprocess.CalledProcessError: If build or push fails.
        FileNotFoundError: If required files are missing.
        ValueError: If run.py is not found or version cannot be determined.
    """
    repo_dir = "."

    # Determine version from setup.py or pyproject.toml
    version = None
    if os.path.exists(f"{repo_dir}/setup.py") or os.path.exists(f"{repo_dir}/pyproject.toml"):
        print("Building Python wheel from setup.py or pyproject.toml...")
        try:
            subprocess.run([sys.executable, "-m", "build", "--outdir", "dist"], check=True, capture_output=True)
            # Extract version from built wheel metadata
            wheel_path = next(Path("dist").glob("*.whl"), None)
            if wheel_path:
                version = importlib.metadata.distribution(wheel_path.stem.split('-')[0]).version
                print(f"Version extracted: {version}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Wheel build failed:\n{e.stdout.decode()}\n{e.stderr.decode()}")
            raise
        except importlib.metadata.PackageNotFoundError:
            logger.error("Could not determine package version from wheel metadata.")
            raise ValueError("Version could not be determined from wheel metadata.")
    else:
        raise ValueError("setup.py or pyproject.toml required to determine version.")

    # Generate Dockerfile
    print("Creating Dockerfile...")
    if not os.path.exists(f"{repo_dir}/run.py"):
        raise ValueError("run.py is required to execute the script sequence. Add it to your repo.")
    with open("Dockerfile", "w") as f:
        f.write("FROM python:3.13-slim\n")
        f.write("WORKDIR /app\n")
        f.write("RUN apt-get update && apt-get install -y git\n")
        if os.path.exists("requirements.txt"):
            f.write("COPY requirements.txt .\n")
            f.write("RUN pip install --no-cache-dir -r requirements.txt\n")
        if wheel_path:
            wheel_filename = os.path.basename(wheel_path)
            shutil.copy(wheel_path, wheel_filename)
            f.write(f"COPY {wheel_filename} .\n")
            f.write(f"RUN pip install {wheel_filename}\n")
        f.write("COPY run.py .\n")
        f.write("CMD [\"python\", \"run.py\"]\n")

    # Build and push Docker image with version tag
    image_uri = f"{config.package_registry_url}/{config.service_name}:{version}"
    print(f"Building Docker image: {image_uri}")
    subprocess.run(["docker", "build", "-t", image_uri, "."], check=True)
    print(f"Pushing Docker image to {config.package_registry_url}...")
    subprocess.run(["docker", "push", image_uri], check=True)

    return image_uri