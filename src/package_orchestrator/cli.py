"""CLI module for package-orchestrator.

This module provides a command-line interface to package the current repository into a Docker image and push it to any
registry, focusing on repos with sequential scripts.
"""

import argparse

from package_orchestrator.builder import build_image
from package_orchestrator.config import Config


def main():
    """Entry point for the package-orchestrator CLI.

    Parses command-line arguments and triggers the packaging process.
    """
    parser = argparse.ArgumentParser(
        description="Package the current repository into a Docker image and push to any registry."
    )
    parser.add_argument(
        "--registry",
        required=True,
        help="Package registry URI (e.g., 'ghcr.io/JENO87/package-orchestrator', 'us-central1-docker.pkg.dev/your-project-id/ml-repo', or 'docker.io/your-username')",
    )
    parser.add_argument(
        "--service-name", default="my-service", help="Name of the target service/image (default: my-service)"
    )
    args = parser.parse_args()

    # Normalize registry to lowercase
    args.registry = args.registry.lower()

    # Create config from CLI args
    config = Config(package_registry_url=args.registry, service_name=args.service_name)

    # Execute the build process
    print(f"Packaging repository with config: {config}")
    image_uri = build_image(config)
    print(f"Successfully built and pushed image: {image_uri}")


if __name__ == "__main__":
    main()
