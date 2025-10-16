package-orchestrator

Version: 0.1.0
License: MIT
Description: A Python package to simplify packaging repositories with sequential scripts into Docker images and pushing them to any registry (e.g., GitHub Packages, GCP Artifact Registry, Docker Hub). Eliminates repetitive packaging code.

Overview
--------

package-orchestrator is a Python tool to package repositories into Docker images for deployment (e.g., Google Cloud Run). It requires a run.py to execute sequential scripts and a pyproject.toml to define the package and dependencies. The resulting wheel and Docker image are pushed to a specified registry.

Requirements
------------

- Python 3.13+
- Docker installed and running (docker --version)
- pip for installing dependencies
- Access to a Docker registry

Installation
------------

Install package-orchestrator in your repository:

    pip install git+https://github.com/JENO87/package-orchestrator.git

This installs dependencies (build, loguru).

Usage
-----

1. Prepare Your Repository

   - Required:
     - run.py: Executes the script sequence.
     - pyproject.toml: Defines the package and dependencies.
   - Optional:
     - Additional scripts or modules used by run.py.

   - Example mock-script-repo structure:
        mock-script-repo/
          run.py            # Executes script sequence
          mock_script_repo/
            __init__.py     # Makes it a Python package
            script1.py      # Example script
            script2.py      # Example script
          pyproject.toml    # Defines package and dependencies
          README.md

   - Example run.py:
        from mock_script_repo import script1, script2

        def main():
            script1.process_data()  # Example function
            script2.generate_report()  # Example function

        if __name__ == "__main__":
            main()

   - Example pyproject.toml:
        [project]
        name = "mock-script-repo"
        version = "0.1.0"
        requires-python = ">=3.13"
        dependencies = ["pandas>=2.0.0"]
        authors = [{name = "Your Name"}]
        description = "A script sequence application"

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.hatch.build.targets.wheel]
        packages = ["mock_script_repo"]

2. Set Up Authentication

   - GitHub Packages:
     1. Create a Personal Access Token (PAT) with repo scope in GitHub Settings.
     2. Set environment variable:
            export GITHUB_PAT=your-token-here

   - GCP Artifact Registry:
     Run:
            gcloud auth configure-docker <region>-docker.pkg.dev
     Example:
            gcloud auth configure-docker us-central1-docker.pkg.dev

   - Docker Hub:
     Log in with:
            docker login
     Or set:
            export DOCKER_PASSWORD=your-password

3. Package the Repository

   Build and push the Docker image:

   - For GitHub Packages:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry ghcr.io/JENO87/my-packages --service-name mock-script

   - For GCP Artifact Registry:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry <region>-docker.pkg.dev/<project-id>/<repository-name> --service-name mock-script
     Example:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry us-central1-docker.pkg.dev/my-project/ml-repo --service-name mock-script

   - For Docker Hub:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry docker.io/<your-username> --service-name mock-script

   - --registry: Registry URI (e.g., ghcr.io/JENO87/my-packages, us-central1-docker.pkg.dev/my-project/ml-repo, docker.io/your-username).
   - --service-name: Image name (e.g., mock-script).

4. Verify the Package

   - The process builds a wheel (dist/mock-script-repo-0.1.0-py3-none-any.whl) and a Docker image (e.g., ghcr.io/JENO87/my-packages/mock-script:0.1.0 or us-central1-docker.pkg.dev/my-project/ml-repo/mock-script:0.1.0).
   - Check the registry:
     - GitHub Packages: https://github.com/JENO87/my-packages/packages
     - GCP Artifact Registry: Use gcloud artifacts repositories list or check the GCP Console.
     - Docker Hub: https://hub.docker.com/r/your-username/mock-script.

5. Create Additional Packages

   For other repositories:
   1. Create a new repo with run.py and pyproject.toml.
   2. Run:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry <your-registry> --service-name <new-service-name>
      Replace <your-registry> with the appropriate URI (e.g., ghcr.io/JENO87/my-packages, us-central1-docker.pkg.dev/my-project/ml-repo, docker.io/your-username).

Steps to Set Up and Run
-----------------------

1. Create the directory structure:
   - Create mock-script-repo/ as the root.
   - Create mock_script_repo/ with an empty __init__.py.
   - Add script1.py and script2.py to mock_script_repo/.
   - Add run.py and pyproject.toml to the root.

        mock-script-repo/
          run.py
          mock_script_repo/
            __init__.py
            script1.py
            script2.py
          pyproject.toml
          README.md

2. Install dependencies:
        pip install uv build loguru hatchling

3. Set up authentication:
   - GitHub Packages:
        export GITHUB_PAT=your-token-here
   - GCP Artifact Registry:
        gcloud auth configure-docker <region>-docker.pkg.dev
     Example:
        gcloud auth configure-docker us-central1-docker.pkg.dev
   - Docker Hub:
        docker login

4. Build and package:
   - For GitHub Packages:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry ghcr.io/JENO87/my-packages --service-name mock-script
   - For GCP Artifact Registry:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry <region>-docker.pkg.dev/<project-id>/<repository-name> --service-name mock-script
     Example:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry us-central1-docker.pkg.dev/my-project/ml-repo --service-name mock-script
   - For Docker Hub:
        uv run python -m build
        uv run python -m package_orchestrator.cli --registry docker.io/<your-username> --service-name mock-script

Expected Output
--------------

- A wheel in dist/mock-script-repo-0.1.0-py3-none-any.whl.
- A Docker image at the specified registry (e.g., ghcr.io/JENO87/my-packages/mock-script:0.1.0, us-central1-docker.pkg.dev/my-project/ml-repo/mock-script:0.1.0, or docker.io/your-username/mock-script:0.1.0).
- The Dockerfile will look like:
        FROM python:3.13-slim
        WORKDIR /app
        RUN apt-get update && apt-get install -y git
        COPY mock-script-repo-0.1.0-py3-none-any.whl .
        RUN pip install mock-script-repo-0.1.0-py3-none-any.whl
        COPY run.py .
        CMD ["python", "run.py"]

Troubleshooting
---------------

- Docker Not Found: Verify Docker is running (docker --version).
- Authentication Failed: Check environment variables (GITHUB_PAT, DOCKER_PASSWORD) or gcloud auth.
- No Wheel Built: Ensure pyproject.toml is valid and includes [tool.hatch.build.targets.wheel] with packages = ["mock_script_repo"].
- Entrypoint Issues: Confirm run.py exists and imports correctly from mock_script_repo.

Contributing
------------

- Fork the repository.
- Create a branch (git checkout -b feature/your-feature).
- Commit changes (git commit -m "Add your feature").
- Push and open a pull request.

License
-------

MIT License - See the [LICENSE] file.

Support
-------

File issues at [GitHub Issues](https://github.com/JENO87/package-orchestrator/issues).