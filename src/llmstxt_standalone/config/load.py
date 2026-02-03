"""Configuration loading from mkdocs.yml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

from llmstxt_standalone.config.derive import nav_to_sections
from llmstxt_standalone.config.model import Config
from llmstxt_standalone.config.plugin import get_llmstxt_config

DEFAULT_SITE_NAME = "Documentation"
DEFAULT_FULL_OUTPUT = "llms-full.txt"


class _PermissiveLoader(yaml.SafeLoader):
    """SafeLoader that ignores unknown Python tags.

    MkDocs extensions like pymdownx.slugs use Python-specific YAML tags
    like !python/object/apply which SafeLoader rejects. This loader
    treats them as raw strings to allow parsing the rest of the config.
    """


def _ignore_unknown(loader: yaml.Loader, tag_suffix: str, node: yaml.Node) -> str:
    """Return the raw tag as a placeholder string."""
    return f"<{node.tag}>"


# Register handler for all Python tags (both full and shorthand forms)
_PermissiveLoader.add_multi_constructor("tag:yaml.org,2002:python/", _ignore_unknown)
_PermissiveLoader.add_multi_constructor("!python/", _ignore_unknown)


class LlmstxtPluginConfig(BaseModel):
    """Pydantic model for llmstxt plugin configuration."""

    markdown_description: str = ""
    full_output: str = DEFAULT_FULL_OUTPUT
    content_selector: str | None = None
    sections: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("sections", mode="before")
    @classmethod
    def validate_sections(cls, v: Any) -> dict[str, list[str]]:
        """Validate sections is a dict with string keys and list[str] values."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError(f"'sections' must be a mapping, got {type(v).__name__}")
        for section_name, pages in v.items():
            if not isinstance(section_name, str):
                raise ValueError(
                    f"'sections' keys must be strings, got {type(section_name).__name__}"
                )
            if not isinstance(pages, list):
                raise ValueError(
                    f"'sections.{section_name}' must be a list of strings, "
                    f"got {type(pages).__name__}"
                )
            for page in pages:
                if not isinstance(page, str):
                    raise ValueError(
                        f"'sections.{section_name}' entries must be strings, "
                        f"got {type(page).__name__}"
                    )
        return v


class MkDocsConfig(BaseModel):
    """Pydantic model for mkdocs.yml top-level fields we care about."""

    site_name: str = DEFAULT_SITE_NAME
    site_description: str = ""
    site_url: str = ""
    nav: list[Any] = Field(default_factory=list)
    use_directory_urls: bool = True

    @field_validator("site_name", mode="before")
    @classmethod
    def coerce_site_name(cls, v: Any) -> str:
        """Coerce None to default."""
        return v if v is not None else DEFAULT_SITE_NAME

    @field_validator("site_description", "site_url", mode="before")
    @classmethod
    def coerce_str_fields(cls, v: Any) -> str:
        """Coerce None to empty string."""
        return v if v is not None else ""

    @field_validator("nav", mode="before")
    @classmethod
    def coerce_nav(cls, v: Any) -> list[Any]:
        """Coerce None to empty list."""
        return v if v is not None else []

    @field_validator("site_url", mode="after")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        """Remove trailing slash from site_url."""
        return v.rstrip("/")


def load_config(config_path: Path) -> Config:
    """Load and resolve configuration from mkdocs.yml.

    Args:
        config_path: Path to mkdocs.yml file.

    Returns:
        Resolved Config object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config is invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            raw = yaml.load(f, Loader=_PermissiveLoader)
    except RecursionError:
        raise ValueError(
            f"Config file has nav structure too deeply nested: {config_path}"
        ) from None

    if not isinstance(raw, dict):
        raise ValueError(f"Config file must be a mapping: {config_path}")

    return _config_from_mkdocs(raw)


def _config_from_mkdocs(raw: dict[str, Any]) -> Config:
    """Build a Config from a parsed mkdocs.yml mapping."""
    try:
        mkdocs = MkDocsConfig.model_validate(raw)
    except ValidationError as e:
        raise ValueError(str(e)) from None

    llmstxt_raw = get_llmstxt_config(raw)

    if llmstxt_raw is not None:
        try:
            plugin = LlmstxtPluginConfig.model_validate(llmstxt_raw)
        except ValidationError as e:
            # Extract the core error message for cleaner output
            raise ValueError(f"llmstxt {e.errors()[0]['msg']}") from None
        sections = plugin.sections
        markdown_description = plugin.markdown_description
        full_output = plugin.full_output
        content_selector = plugin.content_selector
    else:
        sections = nav_to_sections(mkdocs.nav)
        markdown_description = ""
        full_output = DEFAULT_FULL_OUTPUT
        content_selector = None

    return Config(
        site_name=mkdocs.site_name,
        site_description=mkdocs.site_description,
        site_url=mkdocs.site_url,
        markdown_description=markdown_description,
        full_output=full_output,
        content_selector=content_selector,
        sections=sections,
        nav=mkdocs.nav,
        use_directory_urls=mkdocs.use_directory_urls,
    )
