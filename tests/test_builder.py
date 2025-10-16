import os
import shutil
from unittest.mock import patch, MagicMock
import pytest
from builder import build_image
from config import Config

@pytest.fixture
def temp_dir(tmp_path):
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(tmp_path.parent)

def test_build_image_success(temp_dir):
    # Setup mock repo
    with open("run.py", "w") as f:
        f.write("def main(): pass\nif __name__ == '__main__': main()")
    with open("requirements.txt", "w") as f:
        f.write("pandas>=2.0.0")
    with open("setup.py", "w") as f:
        f.write("from setuptools import setup; setup(name='test', version='0.1.0')")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        config = Config(package_registry_url="test-registry", service_name="test-service")
        image_uri = build_image(config)

    assert image_uri == "test-registry/test-service:latest"
    assert os.path.exists("Dockerfile")
    with open("Dockerfile", "r") as f:
        content = f.read()
        assert "COPY run.py" in content
        assert "CMD [\"python\", \"run.py\"]" in content
    assert mock_run.call_count > 0

def test_build_image_no_runpy(temp_dir):
    with open("requirements.txt", "w") as f:
        f.write("pandas>=2.0.0")
    with pytest.raises(ValueError, match="run.py is required"):
        config = Config(package_registry_url="test-registry", service_name="test-service")
        build_image(config)