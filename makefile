.PHONY: install-uv sync install test lint format-check type-check scan-deps build-package publish-package export build-docker-image tag-docker-image push-docker-image clean-docker-image pre-commit clean editable-install ci package

.RECIPEPREFIX = >

# Variables
SRC = src
REGISTRY ?= ghcr.io/JENO87/package-orchestrator
SERVICE_NAME ?= my-service

help:
>@powershell -Command "Get-Content Makefile | Select-String '^[a-zA-Z0-9_-]+:' | ForEach-Object { $$_.Line.Split(':')[0] } | Sort-Object | ForEach-Object { Write-Output $$_ }"

install-uv:
>pip install uv

venv:
>uv venv --python 3.13

activate:
>@powershell -Command "& '.venv\Scripts\Activate.ps1'"

check-env:
>@powershell -Command "Write-Output 'PYTHONPATH: $env:PYTHONPATH'; Write-Output 'Current Dir: $(pwd)'"

run-debug:
>@powershell -Command "$env:PYTHONPATH='$(SRC)'; python -m pdb '$(RUN)'"

sync:
>@uv sync --all-extras

install:
>@make install-uv
>@make sync
>@make editable-install
>@uv run pre-commit install
>@uv run pre-commit autoupdate

test:
>uv run pytest --cov --junitxml=report.xml

lint:
>uv run ruff check . --fix
>uv run mypy .
>uv run pylint src/
>uv run pylint scripts/

format-check:
>uv run pre-commit run ruff-format --all-files
>uv run ruff format --diff .

type-check:
>uv run mypy .

mypy-paths:
>uv run mypy --python-path . scripts

scan-deps:
>trivy fs --format json --output trivy-report.json requirements.txt

pre-commit:
> uv pip install pre-commit ruff
> uv run pre-commit install
> uv run pre-commit autoupdate
> if not exist .gitattributes echo * text=lf > .gitattributes
> if exist src icacls src /grant %USERNAME%:F /T
> if exist tests icacls tests /grant %USERNAME%:F /T
> uv run ruff check . --fix
> uv run pre-commit run end-of-file-fixer --all-files --show-diff-on-failure
> uv run pre-commit run trailing-whitespace --all-files --show-diff-on-failure
> uv run pre-commit run ruff --all-files --hook-stage manual
> uv run pre-commit run ruff-format --all-files --hook-stage manual
> uv run pre-commit run --all-files --hook-stage manual

build-package:
>uv build

publish-package:
>uv publish --registry https://ghcr.io/api/v4/packages/pypi --token $(UV_PUBLISH_TOKEN)

export:
>uv pip compile pyproject.toml -o requirements.txt

build-docker-image:
>docker build -t titanic-classification:${DOCKER_TAG} .

tag-docker-image:
>docker tag titanic-classification:${DOCKER_TAG} ghcr.io/JensNorell/dev-template:${DOCKER_TAG}

push-docker-image:
>docker push ghcr.io/JensNorell/dev-template:${DOCKER_TAG}

clean-docker-image:
>docker rmi titanic-classification:${DOCKER_TAG} ghcr.io/JensNorell/dev-template:${DOCKER_TAG} || true

notify:
>gh issue comment 1 --body "Workflow ${STATUS} for commit ${GITHUB_SHA}. Check details at ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"

clean:
>rm -rf dist *.egg-info .pytest_cache .mypy_cache

ci:
>gh workflow run ci.yml --field branch=$$(git rev-parse --abbrev-ref HEAD)

pr-quality:
>@powershell -Command "if ((git rev-parse --abbrev-ref HEAD) -ne 'development') { Write-Output 'Error: Must be on development branch'; exit 1 }; .\\gh.exe pr create --base quality --title 'Test in quality' --body 'Pull request to quality'"

pr-main:
>@powershell -Command "if ((git rev-parse --abbrev-ref HEAD) -ne 'quality') { Write-Output 'Error: Must be on quality branch'; exit 1 }; .\\gh.exe pr create --base main --title 'Deploy to main' --body 'Pull request to main'"

install-gh:
>powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cli/cli/releases/download/v2.81.0/gh_2.81.0_windows_amd64.zip' -OutFile 'gh.zip'; Expand-Archive -Path 'gh.zip' -DestinationPath '.' -Force; if (Test-Path 'gh_2.81.0_windows_amd64\gh.exe') { Move-Item -Path 'gh_2.81.0_windows_amd64\gh.exe' -Destination '.\gh.exe' -Force }; Remove-Item -Path 'gh.zip' -Force; if (Test-Path 'gh_2.81.0_windows_amd64') { Remove-Item -Path 'gh_2.81.0_windows_amd64' -Recurse -Force }"

# All targets below are for running scripts
setup-branch-protection:
>@powershell -Command "$env:PYTHONPATH='$(SRC)'; uv run python -m scripts/setup_branch_protection.py"

# Package the repository using package_orchestrator CLI
package:
>@uv run python -m package_orchestrator package --registry $(REGISTRY) --service-name $(SERVICE_NAME)
