"""
Pytest configuration and fixtures for the Mergington High School API tests.
"""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original state
    backup = {k: {"participants": v["participants"].copy()} for k, v in activities.items()}
    
    yield
    
    # Restore participants after test
    for activity_name in activities:
        activities[activity_name]["participants"] = backup[activity_name]["participants"].copy()
