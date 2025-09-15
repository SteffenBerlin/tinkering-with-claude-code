"""
Root conftest.py for the project.
Defines pytest configuration and command line options.
"""

import pytest


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--api-key",
        action="store",
        default=None,
        help="Brave API key for integration tests",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as requiring real API integration"
    )