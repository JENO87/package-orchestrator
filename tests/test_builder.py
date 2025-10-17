import subprocess
from unittest.mock import MagicMock, patch

import pytest

from package_orchestrator.builder import build_image
from package_orchestrator.config import Config


@pytest.fixture
def mock_config() -> Config:
    return Config(package_registry_url="test-registry", service_name="test-service")


def test_build_image_success(mock_config: Config) -> None:
    with patch("subprocess.run") as mock_run, patch("importlib.metadata.distribution") as mock_dist:
        mock_dist.return_value.version = "1.0.0"
        mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=0)]
        result = build_image(mock_config)
        assert result == "test-registry/test-service:1.0.0"


def test_build_image_no_run_py(mock_config: Config) -> None:
    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = lambda x: x != "run.py"
        with pytest.raises(ValueError):
            build_image(mock_config)


def test_build_image_build_failure(mock_config: Config) -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker build")
        with pytest.raises(subprocess.CalledProcessError):
            build_image(mock_config)
