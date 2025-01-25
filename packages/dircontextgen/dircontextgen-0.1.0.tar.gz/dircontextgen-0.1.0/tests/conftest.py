# tests/conftest.py
import pytest
from pathlib import Path
from .test_utils import create_test_directory, cleanup_test_directory, TEST_DATA_DIR

def pytest_addoption(parser):
    parser.addoption("--create-test-data", action="store_true",
                     help="Create test data directory without running tests")

def pytest_configure(config):
    if config.getoption("--create-test-data"):
        create_test_directory(debug=True)
        print(f"Test data directory created at: {TEST_DATA_DIR}")
        pytest.exit("Test data directory created")

@pytest.fixture(scope="session", autouse=True)
def create_test_data_once():
    """Create test data directory once per test session"""
    create_test_directory()

@pytest.fixture
def test_data_dir():
    """Fixture providing path to test data directory"""
    return TEST_DATA_DIR

@pytest.fixture
def temp_project(tmp_path):
    """Fixture providing a temporary directory for tests that modify files"""
    project = tmp_path / "temp_project"
    project.mkdir()
    return project