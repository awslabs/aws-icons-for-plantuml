"""Validation tests to ensure the testing infrastructure is properly set up."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestInfrastructureSetup:
    """Test class to validate the testing infrastructure."""
    
    def test_pytest_installed(self):
        """Verify pytest is installed and accessible."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "pytest" in result.stdout
    
    def test_pytest_cov_installed(self):
        """Verify pytest-cov is installed."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pytest-cov"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "pytest-cov" in result.stdout
    
    def test_pytest_mock_installed(self):
        """Verify pytest-mock is installed."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pytest-mock"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "pytest-mock" in result.stdout
    
    def test_directory_structure_exists(self):
        """Verify the testing directory structure is in place."""
        expected_dirs = [
            Path("tests"),
            Path("tests/unit"),
            Path("tests/integration"),
        ]
        
        for dir_path in expected_dirs:
            assert dir_path.exists(), f"Directory {dir_path} does not exist"
            assert dir_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_conftest_exists(self):
        """Verify conftest.py exists with fixtures."""
        conftest_path = Path("tests/conftest.py")
        assert conftest_path.exists(), "conftest.py does not exist"
        
        content = conftest_path.read_text()
        expected_fixtures = [
            "temp_dir",
            "mock_config",
            "sample_yaml_file",
            "sample_svg_content",
            "sample_svg_file",
            "mock_env_vars",
        ]
        
        for fixture in expected_fixtures:
            assert f"def {fixture}" in content, f"Fixture {fixture} not found in conftest.py"
    
    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml exists with proper configuration."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml does not exist"
        
        content = pyproject_path.read_text()
        
        # Check for pytest configuration
        assert "[tool.pytest.ini_options]" in content
        assert "minversion" in content
        assert "addopts" in content
        assert "--cov=scripts" in content
        assert "--cov-fail-under=80" in content
        
        # Check for coverage configuration
        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content
        
        # Check for Poetry scripts
        assert "[tool.poetry.scripts]" in content
        assert 'test = "pytest:main"' in content
        assert 'tests = "pytest:main"' in content
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit marker works correctly."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker works correctly."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker works correctly."""
        assert True
    
    def test_fixtures_work(self, temp_dir, mock_config):
        """Test that fixtures from conftest.py work correctly."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        assert isinstance(mock_config, dict)
        assert "version" in mock_config
        assert mock_config["version"] == "test"
    
    def test_coverage_output_directories(self):
        """Verify coverage output directories can be created."""
        # This test doesn't create the directories, just verifies the config
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()
        
        assert 'directory = "htmlcov"' in content
        assert 'output = "coverage.xml"' in content