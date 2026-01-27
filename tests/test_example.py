"""Example tests for the llmstxt_gen package."""

from llmstxt_gen import __version__


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.1.0"
