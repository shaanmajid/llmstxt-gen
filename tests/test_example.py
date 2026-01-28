"""Example tests for the llmstxt_standalone package."""

from llmstxt_standalone import __version__


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.1.0"
