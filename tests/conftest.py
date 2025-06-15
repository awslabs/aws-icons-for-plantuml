"""Shared pytest fixtures and configuration for all tests."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files.
    
    Yields:
        Path: Path to the temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config() -> dict:
    """Provide a mock configuration dictionary.
    
    Returns:
        dict: Mock configuration for testing
    """
    return {
        "version": "test",
        "source_dir": "source",
        "dist_dir": "dist",
        "icons": [
            {
                "name": "TestIcon",
                "category": "TestCategory",
                "path": "test/path/icon.svg"
            }
        ]
    }


@pytest.fixture
def sample_yaml_file(temp_dir: Path) -> Path:
    """Create a sample YAML configuration file.
    
    Args:
        temp_dir: Temporary directory fixture
        
    Returns:
        Path: Path to the created YAML file
    """
    yaml_path = temp_dir / "test_config.yml"
    config_data = {
        "version": "1.0",
        "icons": ["icon1", "icon2", "icon3"]
    }
    with open(yaml_path, 'w') as f:
        yaml.dump(config_data, f)
    return yaml_path


@pytest.fixture
def sample_svg_content() -> str:
    """Provide sample SVG content for testing.
    
    Returns:
        str: Sample SVG XML content
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" fill="blue"/>
</svg>"""


@pytest.fixture
def sample_svg_file(temp_dir: Path, sample_svg_content: str) -> Path:
    """Create a sample SVG file.
    
    Args:
        temp_dir: Temporary directory fixture
        sample_svg_content: Sample SVG content fixture
        
    Returns:
        Path: Path to the created SVG file
    """
    svg_path = temp_dir / "test_icon.svg"
    svg_path.write_text(sample_svg_content)
    return svg_path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing.
    
    Args:
        monkeypatch: pytest monkeypatch fixture
        
    Returns:
        dict: Dictionary of mocked environment variables
    """
    env_vars = {
        "TEST_VAR": "test_value",
        "DEBUG": "true",
        "CONFIG_PATH": "/test/config/path"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up any test files created during test execution."""
    yield
    # Cleanup logic here if needed
    test_patterns = ["test_*.tmp", "*.test"]
    for pattern in test_patterns:
        for file in Path(".").glob(pattern):
            if file.exists():
                file.unlink()


@pytest.fixture
def capture_logs(caplog):
    """Capture log messages during tests.
    
    Args:
        caplog: pytest caplog fixture
        
    Returns:
        caplog: Configured caplog fixture
    """
    caplog.set_level("DEBUG")
    return caplog


@pytest.fixture
def mock_http_response(mocker):
    """Mock HTTP responses for testing.
    
    Args:
        mocker: pytest-mock mocker fixture
        
    Returns:
        Mock: Mocked response object
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "Mock response content"
    mock_response.json.return_value = {"status": "success"}
    return mock_response