"""Builder module for package-orchestrator.

This module packages the current repository into a Docker image and pushes it to a specified registry.
It builds a wheel if setup.py exists and uses run.py to execute sequential scripts.
"""
import subprocess
import os
from package_orchestrator.config import Config
from pathlib import Path

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
        subprocess.run(["python", "-m", "build", "--outdir", "dist"], check=True)
        wheel_path = next(Path("dist").glob("*.whl"), None)
        if wheel_path:
            print(f"Wheel created at: {wheel_path}")
        else:
            print("No wheel file generated; using raw files.")

    # Generate Dockerfile with run.py as entrypoint
    print("Creating Dockerfile...")
    if not os.path.exists(f"{repo_dir}/run.py"):
        raise ValueError("run.py is required to execute the script sequence. Add it to your repo.")
    dockerfile = f"""
    FROM python:3.9-slim
    WORKDIR /app
    """
    if os.path.exists("requirements.txt"):
        dockerfile += """
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        """
    if wheel_path:
        dockerfile += f"COPY {wheel_path} .\nRUN pip install {wheel_path.name}\n"
    else:
        dockerfile += "COPY . .\n"
    dockerfile += """
    COPY run.py .
    CMD ["python", "run.py"]
    """
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

    # Authenticate with the package registry based on URI
    image_uri = f"{config.package_registry_url}/{config.service_name}:latest"
    registry_host = config.package_registry_url.split("/")[0]  # e.g., 'ghcr.io', 'us-central1-docker.pkg.dev', 'docker.io'
    if registry_host == "ghcr.io" and os.environ.get("GITHUB_PAT"):
        print("Authenticating with GitHub Packages...")
        subprocess.run(["docker", "login", registry_host, "-u", "JENO87", "-p", os.environ.get("GITHUB_PAT")], check=True)
    elif registry_host == "docker.io" and os.environ.get("DOCKER_PASSWORD"):
        print("Authenticating with Docker Hub...")
        subprocess.run(["docker", "login", "-u", os.environ.get("DOCKER_USERNAME", "your-username"), "-p", os.environ.get("DOCKER_PASSWORD")], check=True)
    # GCP assumes pre-configured gcloud authentication

    # Build and push the Docker image
    print(f"Building Docker image: {image_uri}")
    subprocess.run(["docker", "build", "-t", image_uri, "."], check=True)
    print(f"Pushing Docker image to {config.package_registry_url}...")
    subprocess.run(["docker", "push", image_uri], check=True)

    return image_uri