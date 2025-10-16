"""Configuration module for package-orchestrator.

This file defines the Config dataclass to hold settings for packaging the current repository.
It supports any registry (e.g., GitHub Packages, GCP Artifact Registry, Docker Hub).
"""
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration for packaging the current repository.

    Args:
        package_registry_url: Package registry path (e.g., 'ghcr.io/JENO87/package-orchestrator' or any registry URI).
        service_name: Name of the target service/image (e.g., 'my-service').
    """
    package_registry_url: str
    service_name: str = "my-service"