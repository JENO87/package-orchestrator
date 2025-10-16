import sys
from unittest.mock import patch, MagicMock
import pytest
from cli import main
from config import Config

@patch("argparse._sys.argv", ["package_orchestrator", "package", "--registry", "test-registry", "--service-name", "test-service"])
@patch("package_orchestrator.builder.build_image")
def test_main_success(mock_build_image):
    mock_build_image.return_value = "test-registry/test-service:latest"
    with patch("builtins.print") as mock_print:
        main()
        mock_print.assert_any_call("Packaging repository with config: Config(package_registry='test-registry', service_name='test-service')")
        mock_print.assert_any_call("Successfully built and pushed image: test-registry/test-service:latest")

@patch("argparse._sys.argv", ["package_orchestrator", "package", "--registry", "test-registry"])
def test_main_default_service_name():
    with patch("package_orchestrator.builder.build_image") as mock_build_image:
        mock_build_image.return_value = "test-registry/my-service:latest"
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_any_call("Packaging repository with config: Config(package_registry='test-registry', service_name='my-service')")

@patch("argparse.ArgumentParser.parse_args")
def test_main_missing_registry(mock_parse_args):
    mock_parse_args.side_effect = SystemExit
    with pytest.raises(SystemExit):
        main()