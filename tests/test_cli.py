import os
from unittest.mock import patch, MagicMock
import pytest
from package_orchestrator.cli import main
from package_orchestrator.config import Config

@pytest.fixture
def temp_dir(tmp_path):
    os.chdir(tmp_path)
    with open("run.py", "w") as f:
        f.write("def main(): pass\nif __name__ == '__main__': main()")
    yield tmp_path
    os.chdir(tmp_path.parent)

@patch("subprocess.run")
def test_main_success(mock_subprocess_run, temp_dir):
    with patch("argparse._sys.argv", ["package_orchestrator", "--registry", "test-registry", "--service-name", "test-service"]):
        with patch("package_orchestrator.builder.build_image") as mock_build_image:
            mock_build_image.return_value = "test-registry/test-service:latest"
            mock_subprocess_run.side_effect = [
                MagicMock(returncode=0),  # Mock docker build
                MagicMock(returncode=0)   # Mock docker push
            ]
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Packaging repository with config: Config(package_registry_url='test-registry', service_name='test-service')")
                mock_print.assert_any_call("Successfully built and pushed image: test-registry/test-service:latest")

@patch("subprocess.run")
def test_main_default_service_name(mock_subprocess_run, temp_dir):
    with patch("argparse._sys.argv", ["package_orchestrator", "--registry", "test-registry"]):
        with patch("package_orchestrator.builder.build_image") as mock_build_image:
            mock_build_image.return_value = "test-registry/my-service:latest"
            mock_subprocess_run.side_effect = [
                MagicMock(returncode=0),  # Mock docker build
                MagicMock(returncode=0)   # Mock docker push
            ]
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Packaging repository with config: Config(package_registry_url='test-registry', service_name='my-service')")

@patch("argparse.ArgumentParser.parse_args")
def test_main_missing_registry(mock_parse_args):
    mock_parse_args.side_effect = SystemExit
    with pytest.raises(SystemExit):
        main()