"""Deployment module for package-orchestrator.

This module handles deploying a packaged image to Cloud Run or Vertex AI. It is designed for both GitHub Packages
(current) and GCP Artifact Registry (future), with detailed comments for team understanding and generic support for any
repo type.
"""

import os
import subprocess

from config import Config
from google.cloud import aiplatform, run_v2


def authenticate_registry(config: Config) -> None:
    """Authenticates with the package registry based on the environment.

    Args:
        config: Config object with registry details.

    Notes
    -----
        - Uses GITHUB_PAT for GitHub Packages.
        - Uses gcloud for GCP Artifact Registry (requires GCP access).
    """
    if "ghcr.io" in config.package_registry:
        print("Authenticating with GitHub Packages...")
        subprocess.run(["docker", "login", "ghcr.io", "-u", "JENO87", "-p", os.environ.get("GITHUB_PAT")], check=True)
    elif config.project_id:
        print("Authenticating with GCP Artifact Registry...")
        subprocess.run(["gcloud", "auth", "configure-docker", f"{config.region}-docker.pkg.dev"], check=True)


def deploy_cloud_run(config: Config, image_uri: str) -> str:
    """Deploys the image to Cloud Run for any repository type.

    Args:
        config: Config with GCP project and region details.
        image_uri: Full URI of the Docker image to deploy.

    Returns
    -------
        str: The URL of the deployed Cloud Run service.

    Raises
    ------
        ValueError: If GCP config is missing.
    """
    if not config.project_id or not config.region:
        raise ValueError("project_id and region are required for Cloud Run deployment.")

    client = run_v2.ServicesClient()
    service_name = f"projects/{config.project_id}/locations/{config.region}/services/{config.service_name}"

    service = {
        "name": service_name,
        "template": {
            "containers": [{"image": image_uri, "ports": [{"container_port": 8080}]}],
            "scaling": {"min_instance_count": 0, "max_instance_count": 10},
        },
        "traffic": [{"percent": 100, "revision": ""}],
    }

    print(f"Deploying to Cloud Run: {service_name}")
    response = client.create_service(parent=f"projects/{config.project_id}/locations/{config.region}", service=service)
    print(f"Operation initiated: {response.operation.name}")
    result = response.result()  # Synchronous for simplicity
    service_url = f"https://{result.name.split('/')[-1]}-{config.region}.run.app"
    print(f"Deployed at: {service_url}")
    return service_url


def deploy_vertex_ai(config: Config, image_uri: str) -> str:
    """Deploys the image as a Vertex AI Custom Job (placeholder for any repo type).

    Args:
        config: Config with GCP project and region details.
        image_uri: Full URI of the Docker image to deploy.

    Returns
    -------
        str: Empty string (no URL for batch jobs yet).

    Notes
    -----
        Requires GCP access to fully implement; currently a placeholder.
    """
    if not config.project_id or not config.region:
        print("Vertex AI deployment skipped due to missing GCP config.")
        return ""

    aiplatform.init(project=config.project_id, location=config.region)
    job = aiplatform.CustomJob(
        display_name=config.service_name,
        worker_pool_specs=[
            {"machine_spec": {"machine_type": "n1-standard-4"}, "container_spec": {"image_uri": image_uri}}
        ],
    )
    print("Submitting Vertex AI job...")
    job.run(sync=True)
    print("Vertex AI job completed. Check logs in Vertex AI console.")
    return ""


def deploy_service(config: Config) -> str:
    """Orchestrates deployment to the specified target for any repository.

    Args:
        config: Config with deployment details.

    Returns
    -------
        str: URL of the deployed service or empty string if not applicable.
    """
    # Validate deployment target
    if config.deploy_target not in ["cloud-run", "vertex-ai"]:
        raise ValueError(f"Unsupported deploy_target: {config.deploy_target}")

    # Authenticate with the registry
    authenticate_registry(config)

    # Build the image URI
    image_uri = f"{config.package_registry}/{config.service_name}:latest"
    print(f"Deploying image: {image_uri}")

    # Dispatch to appropriate deployment function
    if config.deploy_target == "cloud-run":
        return deploy_cloud_run(config, image_uri)
    elif config.deploy_target == "vertex-ai":
        return deploy_vertex_ai(config, image_uri)


# Example usage (manual run, skip without GCP)
if __name__ == "__main__":
    config = Config(
        repo_url="https://github.com/JENO87/sample-repo.git",
        project_id="your-project-id",  # Set when on GCP
        region="us-central1",  # Set when on GCP
        package_registry="ghcr.io/JENO87/package-orchestrator",
        deploy_target="cloud-run",
    )
    deploy_service(config)  # Will fail without GCP; test builder.py first
