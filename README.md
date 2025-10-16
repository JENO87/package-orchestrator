Title: package-orchestrator

Version: 0.1.0
License: MIT
Description: A generic Python package to simplify packaging repositories with sequential scripts into a Docker image and push it to any registry (e.g., GitHub Packages, GCP Artifact Registry, Docker Hub). This repo eliminates repetitive packaging code and focuses solely on packaging.

Overview
--------
package-orchestrator is a Python package you can install in any repository to package it into a Docker image. It assumes the repo contains sequential scripts executed via a run.py file and builds a containerized version, including a Python wheel for importing into other repos (e.g., a deploy repo). The package is pushed to a specified registry, with deployment handled separately.

Requirements
------------
- Python: 3.13 or higher
- Docker: Installed and running locally (verify with docker --version)
- pip: For installing the package

Installation
------------
To use package-orchestrator in your target repository, install it as a dependency:

  pip install git+https://github.com/JENO87/package-orchestrator.git

This installs the package and its dependencies (e.g., pydantic, python-dotenv).

Usage
-----
### 1. Prepare Your Repository
- Ensure your repo has a compatible structure:
  - Required: run.py to execute the sequence of scripts (see example below).
  - Required: setup.py to define your Python package for a wheel (see template below; needed for importing into other repos).
  - Optional: requirements.txt for dependencies (e.g., libraries used by your scripts).
- Example my-script-repo structure:
  my-script-repo/
    run.py            # Executes the script sequence (required)
    script1.py        # First script in sequence
    script2.py        # Second script in sequence
    setup.py          # Defines your package (required for wheel)
    requirements.txt  # Lists dependencies (optional)
    README.md

- Example run.py:
  Create run.py in your target repo to orchestrate your script sequence:
    # run.py
    import script1
    import script2

    def main():
        script1.process_data()  # Example function
        script2.generate_report()  # Example function

    if __name__ == "__main__":
        main()

- Template for setup.py (Required):
  Create setup.py in your target repo with the following content, customizing as needed:
    from setuptools import setup, find_packages

    setup(
        name="my-script-repo",    # Name of your package
        version="0.1.0",          # Version of your package
        packages=find_packages(), # Automatically finds Python packages
        install_requires=[        # List dependencies (can mirror requirements.txt)
            "pandas>=2.0.0",      # Example dependency
        ],
        author="Your Name",       # Your name or team
        description="A script sequence application",
    )
  - Notes: Replace my-script-repo with your package name and adjust install_requires based on requirements.txt. This is required to generate a wheel for importing into your deploy repo.

### 2. Set Up Authentication
- For any registry, set up authentication based on the registry type:
  - GitHub Packages: Create a Personal Access Token (PAT) with repo scope:
    1. Go to GitHub > Settings > Developer Settings > Personal Access Tokens > Generate New Token.
    2. Copy the token and set it as an environment variable:
       export GITHUB_PAT=your-token-here
    - Or add it to a .env file:
      GITHUB_PAT=your-token-here
  - GCP Artifact Registry: Use gcloud authentication (run gcloud auth configure-docker before packaging).
  - Docker Hub: Log in with docker login and set DOCKER_PASSWORD:
    export DOCKER_PASSWORD=your-password
- The CLI will attempt to authenticate using the appropriate environment variable or skip if not needed.

### 3. Package the Repository
- In your repository's root directory, run the CLI command:
  python -m package_orchestrator package --registry <your-registry> --service-name my-script
  - --registry: The package registry URI where the Docker image will be pushed (e.g., ghcr.io/JENO87/package-orchestrator, us-central1-docker.pkg.dev/your-project-id/ml-repo, or docker.io/your-username).
  - --service-name: The name of the service/image (e.g., my-script; defaults to my-service).

### 4. Verify the Package
- The process builds a Python wheel (required via setup.py) and a Docker image, then pushes it to the specified registry.
- Check your registry for the image:
  - GitHub Packages: https://github.com/JENO87/package-orchestrator/packages/container/package-orchestrator/my-script
  - GCP Artifact Registry: Use gcloud artifacts repositories list and browse the UI.
  - Docker Hub: https://hub.docker.com/r/your-username/my-script
- The image will be available at <your-registry>/my-script:latest, and the wheel can be imported (e.g., import my-script-repo in your deploy repo).

### 5. Create Additional Packages
- To package other repositories with sequential scripts:
  1. Create a new directory for each repo (e.g., my-other-script-repo).
  2. Add run.py with your script sequence logic.
  3. Add setup.py with the appropriate package name and dependencies.
  4. Optionally add requirements.txt for dependencies.
  5. Navigate to the new repo directory and run:
     python -m package_orchestrator package --registry <your-registry> --service-name my-other-script
  - Repeat for each new repo, adjusting registry and service-name as needed. Ensure each setup.py has a unique package name to avoid conflicts when importing.

Troubleshooting
--------------
- Docker Not Found: Ensure Docker is installed and running (docker --version).
- Authentication Failed: Verify the correct environment variable is set (e.g., GITHUB_PAT, DOCKER_PASSWORD) or use gcloud auth for GCP.
- No Wheel Built: Ensure setup.py exists and is correctly configured.
- Entrypoint Issues: Ensure run.py exists and executes your script sequence. Add dependencies to requirements.txt if needed.

Contributing
------------
- Fork the repository.
- Create a branch (git checkout -b feature/your-feature).
- Commit changes (git commit -m "Add your feature").
- Push and open a pull request.

License
-------
MIT License - See the [LICENSE] file for details.

Support
-------
For issues, use the [GitHub Issues] page[](https://github.com/JENO87/package-orchestrator/issues).
