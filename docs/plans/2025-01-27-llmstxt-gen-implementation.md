# llmstxt-gen Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool that generates llms.txt and llms-full.txt from built HTML documentation.

**Architecture:** Typer CLI → config loader (mkdocs.yml) → HTML converter (BeautifulSoup + markdownify) → file writer. Four modules with single responsibilities, TDD approach.

**Tech Stack:** Python 3.10+, Typer, PyYAML, BeautifulSoup4, markdownify, mdformat

---

## Task 1: Project Setup

**Files:**
- Modify: `pyproject.toml`
- Rename: `src/python_template/` → `src/llmstxt_gen/`
- Modify: `src/llmstxt_gen/__init__.py`
- Modify: `README.md`
- Delete: `src/llmstxt_gen/__pycache__/`

**Step 1: Rename the source directory**

```bash
cd ~/code/llmstxt-gen
rm -rf src/python_template/__pycache__
mv src/python_template src/llmstxt_gen
```

**Step 2: Update pyproject.toml**

Replace entire contents with:

```toml
[project]
name = "llmstxt-gen"
version = "0.1.0"
description = "Generate llms.txt from built HTML documentation"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
keywords = ["llms", "documentation", "markdown", "mkdocs"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Documentation",
    "Typing :: Typed",
]

authors = [{ name = "Shaan Khosla" }]

dependencies = [
    "typer>=0.9.0",
    "pyyaml>=6.0",
    "beautifulsoup4>=4.12",
    "markdownify>=0.11",
    "mdformat>=0.7",
    "mdformat-tables>=1.0",
]

[project.scripts]
llmstxt-gen = "llmstxt_gen.cli:app"

[project.urls]
Repository = "https://github.com/shaankhosla/llmstxt-gen"

[dependency-groups]
dev = [
    { include-group = "lint" },
    { include-group = "test" },
]
lint = ["ruff>=0.9.0"]
test = ["pytest>=8.0.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Update __init__.py**

```python
"""llmstxt-gen: Generate llms.txt from built HTML documentation."""

__version__ = "0.1.0"
```

**Step 4: Create placeholder modules**

Create `src/llmstxt_gen/__main__.py`:
```python
"""Allow running as python -m llmstxt_gen."""

from llmstxt_gen.cli import app

if __name__ == "__main__":
    app()
```

Create `src/llmstxt_gen/cli.py`:
```python
"""Command-line interface."""

import typer

app = typer.Typer(help="Generate llms.txt from built HTML documentation.")


@app.command()
def main() -> None:
    """Generate llms.txt and llms-full.txt."""
    typer.echo("Not implemented yet")
    raise typer.Exit(1)
```

Create `src/llmstxt_gen/config.py`:
```python
"""Configuration loading and resolution."""
```

Create `src/llmstxt_gen/convert.py`:
```python
"""HTML to Markdown conversion."""
```

Create `src/llmstxt_gen/generate.py`:
```python
"""Main generation orchestration."""
```

**Step 5: Update README.md**

```markdown
# llmstxt-gen

Generate `/llms.txt` and `/llms-full.txt` from built HTML documentation, following the [llms.txt spec](https://llmstxt.org/).

## Installation

```bash
uv tool install llmstxt-gen
# or
pipx install llmstxt-gen
```

## Usage

```bash
# Run from project root (looks for mkdocs.yml + site/)
llmstxt-gen

# Explicit paths
llmstxt-gen --config mkdocs.yml --site-dir ./build
```

## Configuration

Add llmstxt config to your `mkdocs.yml`:

```yaml
plugins:
  - llmstxt:
      markdown_description: |
        Extra context for LLMs...
      sections:
        Getting Started:
          - index.md
          - install.md
```

If no `llmstxt` plugin config exists, sections are derived from `nav` automatically.

## License

MIT
```

**Step 6: Install dependencies and verify**

```bash
cd ~/code/llmstxt-gen
uv sync
uv run llmstxt-gen --help
```

Expected: Help text displays

**Step 7: Commit**

```bash
git add -A
git commit -m "chore: set up llmstxt-gen project structure"
```

---

## Task 2: HTML to Markdown Conversion (convert.py)

**Files:**
- Modify: `src/llmstxt_gen/convert.py`
- Create: `tests/test_convert.py`
- Create: `tests/fixtures/sample.html`

**Step 1: Create test fixture**

Create `tests/fixtures/sample.html`:
```html
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<article class="md-content__inner">
  <h1>Test Page</h1>
  <p>This is a <strong>test</strong> paragraph.</p>
  <a href="#section" class="headerlink">¶</a>
  <img src="image.png" alt="test">
  <pre><code class="language-python">print("hello")</code></pre>
</article>
</body>
</html>
```

**Step 2: Write failing test for html_to_markdown**

Create `tests/test_convert.py`:
```python
"""Tests for HTML to Markdown conversion."""

from pathlib import Path

from llmstxt_gen.convert import html_to_markdown


def test_html_to_markdown_basic():
    html = """
    <article>
        <h1>Title</h1>
        <p>This is <strong>bold</strong> text.</p>
    </article>
    """
    result = html_to_markdown(html)
    assert "# Title" in result
    assert "**bold**" in result


def test_html_to_markdown_removes_images():
    html = """
    <article>
        <p>Text</p>
        <img src="test.png" alt="test">
    </article>
    """
    result = html_to_markdown(html)
    assert "img" not in result.lower()
    assert "test.png" not in result


def test_html_to_markdown_removes_headerlinks():
    html = """
    <article>
        <h2>Section<a href="#section" class="headerlink">¶</a></h2>
    </article>
    """
    result = html_to_markdown(html)
    assert "¶" not in result
    assert "headerlink" not in result


def test_html_to_markdown_preserves_code_language():
    html = """
    <article>
        <pre><code class="language-python">print("hello")</code></pre>
    </article>
    """
    result = html_to_markdown(html)
    assert "```python" in result
    assert 'print("hello")' in result
```

**Step 3: Run tests to verify they fail**

```bash
cd ~/code/llmstxt-gen
uv run pytest tests/test_convert.py -v
```

Expected: FAIL with ImportError

**Step 4: Implement convert.py**

```python
"""HTML to Markdown conversion."""

from __future__ import annotations

from itertools import chain

import mdformat
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import ATX, MarkdownConverter


def _should_remove(tag: Tag) -> bool:
    """Check if a tag should be removed during autoclean."""
    if tag.name in {"img", "svg"}:
        return True
    if tag.name == "a" and tag.img:
        return True
    classes = tag.get("class") or ()
    if tag.name == "a" and "headerlink" in classes:
        return True
    if "twemoji" in classes:
        return True
    if "tabbed-labels" in classes:
        return True
    return False


def _autoclean(soup: BeautifulSoup) -> None:
    """Remove unwanted elements from HTML."""
    for element in soup.find_all(_should_remove):
        element.decompose()

    # Unwrap autoref elements
    for element in soup.find_all("autoref"):
        element.replace_with(NavigableString(element.get_text()))

    # Remove line numbers from code blocks
    for element in soup.find_all("table", attrs={"class": "highlighttable"}):
        code = element.find("code")
        if code:
            element.replace_with(
                BeautifulSoup(f"<pre>{code.get_text()}</pre>", "html.parser")
            )


def _get_language(tag: Tag) -> str:
    """Extract language from code block classes."""
    classes = chain(
        tag.get("class") or (),
        (tag.parent.get("class") or ()) if tag.parent else (),
    )
    for css_class in classes:
        if css_class.startswith("language-"):
            return css_class[9:]
    return ""


# Converter with mkdocs-llmstxt-compatible settings
_converter = MarkdownConverter(
    bullets="-",
    code_language_callback=_get_language,
    escape_underscores=False,
    heading_style=ATX,
)


def html_to_markdown(html: str, content_selector: str | None = None) -> str:
    """Convert HTML to clean Markdown.

    Args:
        html: Raw HTML content.
        content_selector: Optional CSS selector for main content.
            Defaults to Material for MkDocs selectors.

    Returns:
        Cleaned Markdown text.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find main content
    if content_selector:
        content = soup.select_one(content_selector)
    else:
        content = (
            soup.select_one(".md-content__inner")
            or soup.select_one("article")
            or soup.select_one("main")
            or soup
        )

    if content is None:
        return ""

    _autoclean(content)
    md = _converter.convert_soup(content)
    return mdformat.text(md, options={"wrap": "no"}, extensions=("tables",))
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_convert.py -v
```

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/llmstxt_gen/convert.py tests/test_convert.py tests/fixtures/
git commit -m "feat: add HTML to Markdown conversion"
```

---

## Task 3: Config Loading (config.py)

**Files:**
- Modify: `src/llmstxt_gen/config.py`
- Create: `tests/test_config.py`
- Create: `tests/fixtures/mkdocs_with_llmstxt.yml`
- Create: `tests/fixtures/mkdocs_nav_only.yml`

**Step 1: Create test fixtures**

Create `tests/fixtures/mkdocs_with_llmstxt.yml`:
```yaml
site_name: Test Site
site_description: A test site
site_url: https://test.com/

nav:
  - Home: index.md
  - Guide:
    - Install: install.md

plugins:
  - search
  - llmstxt:
      markdown_description: |
        Custom description for LLMs.
      full_output: llms-full.txt
      sections:
        Getting Started:
          - index.md
          - install.md
```

Create `tests/fixtures/mkdocs_nav_only.yml`:
```yaml
site_name: Test Site
site_description: A test site
site_url: https://test.com/

nav:
  - Home: index.md
  - Guide:
    - Install: install.md
    - Usage: usage.md

plugins:
  - search
```

**Step 2: Write failing tests**

Create `tests/test_config.py`:
```python
"""Tests for configuration loading."""

from pathlib import Path

import pytest

from llmstxt_gen.config import Config, load_config

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_config_with_llmstxt_plugin():
    config = load_config(FIXTURES / "mkdocs_with_llmstxt.yml")

    assert config.site_name == "Test Site"
    assert config.site_description == "A test site"
    assert config.site_url == "https://test.com"
    assert "Custom description" in config.markdown_description
    assert config.full_output == "llms-full.txt"
    assert "Getting Started" in config.sections
    assert config.sections["Getting Started"] == ["index.md", "install.md"]


def test_load_config_nav_fallback():
    config = load_config(FIXTURES / "mkdocs_nav_only.yml")

    assert config.site_name == "Test Site"
    # Sections derived from nav
    assert "Home" in config.sections or "Guide" in config.sections


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/mkdocs.yml"))


def test_get_page_title():
    config = load_config(FIXTURES / "mkdocs_with_llmstxt.yml")

    assert config.get_page_title("index.md") == "Home"
    assert config.get_page_title("install.md") == "Install"
    # Fallback for unknown pages
    assert "unknown" in config.get_page_title("unknown-page.md").lower()
```

**Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL with ImportError

**Step 4: Implement config.py**

```python
"""Configuration loading and resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Resolved configuration for llmstxt generation."""

    site_name: str
    site_description: str
    site_url: str
    markdown_description: str
    full_output: str
    content_selector: str | None
    sections: dict[str, list[str]]
    nav: list[Any]

    def get_page_title(self, md_path: str) -> str:
        """Find the title for a page from the nav structure."""
        title = self._search_nav(self.nav, md_path)
        if title:
            return title
        # Fallback: derive from filename
        return md_path.replace(".md", "").replace("-", " ").replace("/", " - ").title()

    def _search_nav(self, items: list[Any], md_path: str) -> str | None:
        """Recursively search nav for a page title."""
        for item in items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and value == md_path:
                        return key
                    if isinstance(value, list):
                        result = self._search_nav(value, md_path)
                        if result:
                            return result
        return None


def load_config(config_path: Path) -> Config:
    """Load and resolve configuration from mkdocs.yml.

    Args:
        config_path: Path to mkdocs.yml file.

    Returns:
        Resolved Config object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.load(f, Loader=yaml.BaseLoader)

    site_name = raw.get("site_name", "Documentation")
    site_description = raw.get("site_description", "")
    site_url = raw.get("site_url", "").rstrip("/")
    nav = raw.get("nav", [])

    # Extract llmstxt plugin config if present
    llmstxt_config = _get_llmstxt_config(raw)

    if llmstxt_config:
        markdown_description = llmstxt_config.get("markdown_description", "")
        full_output = llmstxt_config.get("full_output", "llms-full.txt")
        content_selector = llmstxt_config.get("content_selector")
        sections = llmstxt_config.get("sections", {})
    else:
        # Fallback: derive sections from nav
        markdown_description = ""
        full_output = "llms-full.txt"
        content_selector = None
        sections = _nav_to_sections(nav)

    return Config(
        site_name=site_name,
        site_description=site_description,
        site_url=site_url,
        markdown_description=markdown_description,
        full_output=full_output,
        content_selector=content_selector,
        sections=sections,
        nav=nav,
    )


def _get_llmstxt_config(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Extract llmstxt plugin config from mkdocs.yml plugins list."""
    plugins = raw.get("plugins", [])
    for plugin in plugins:
        if isinstance(plugin, dict) and "llmstxt" in plugin:
            return plugin["llmstxt"]
        if plugin == "llmstxt":
            return {}
    return None


def _nav_to_sections(nav: list[Any]) -> dict[str, list[str]]:
    """Convert nav structure to sections dict."""
    sections: dict[str, list[str]] = {}

    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    # Top-level page, add to "Pages" section
                    sections.setdefault("Pages", []).append(value)
                elif isinstance(value, list):
                    # Section with children
                    pages = _extract_pages(value)
                    if pages:
                        sections[key] = pages

    return sections


def _extract_pages(items: list[Any]) -> list[str]:
    """Extract page paths from nav items."""
    pages = []
    for item in items:
        if isinstance(item, str):
            pages.append(item)
        elif isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    pages.append(value)
                elif isinstance(value, list):
                    pages.extend(_extract_pages(value))
    return pages
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_config.py -v
```

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/llmstxt_gen/config.py tests/test_config.py tests/fixtures/*.yml
git commit -m "feat: add config loading with nav fallback"
```

---

## Task 4: Generation Orchestration (generate.py)

**Files:**
- Modify: `src/llmstxt_gen/generate.py`
- Create: `tests/test_generate.py`
- Create: `tests/fixtures/site/index.html`
- Create: `tests/fixtures/site/install/index.html`

**Step 1: Create test fixtures**

Create `tests/fixtures/site/index.html`:
```html
<!DOCTYPE html>
<html>
<head><title>Home</title></head>
<body>
<article>
  <h1>Welcome</h1>
  <p>This is the home page.</p>
</article>
</body>
</html>
```

Create `tests/fixtures/site/install/index.html`:
```html
<!DOCTYPE html>
<html>
<head><title>Install</title></head>
<body>
<article>
  <h1>Installation</h1>
  <p>Install with pip.</p>
  <pre><code class="language-bash">pip install example</code></pre>
</article>
</body>
</html>
```

**Step 2: Write failing tests**

Create `tests/test_generate.py`:
```python
"""Tests for generation orchestration."""

from pathlib import Path

from llmstxt_gen.config import load_config
from llmstxt_gen.generate import generate_llms_txt, md_path_to_html_path, md_path_to_md_url


FIXTURES = Path(__file__).parent / "fixtures"


def test_md_path_to_html_path():
    site_dir = Path("/site")

    assert md_path_to_html_path(site_dir, "index.md") == Path("/site/index.html")
    assert md_path_to_html_path(site_dir, "install.md") == Path("/site/install/index.html")
    assert md_path_to_html_path(site_dir, "guide/intro.md") == Path("/site/guide/intro/index.html")


def test_md_path_to_md_url():
    site_url = "https://example.com"

    assert md_path_to_md_url(site_url, "index.md") == "https://example.com/index.md"
    assert md_path_to_md_url(site_url, "install.md") == "https://example.com/install/index.md"


def test_generate_llms_txt(tmp_path: Path):
    config = load_config(FIXTURES / "mkdocs_with_llmstxt.yml")

    llms_txt, llms_full_txt = generate_llms_txt(
        config=config,
        site_dir=FIXTURES / "site",
    )

    # Check llms.txt structure
    assert "# Test Site" in llms_txt
    assert "> A test site" in llms_txt
    assert "Custom description" in llms_txt
    assert "## Getting Started" in llms_txt
    assert "[Home](" in llms_txt

    # Check llms-full.txt structure
    assert "# Test Site" in llms_full_txt
    assert "Welcome" in llms_full_txt or "Installation" in llms_full_txt
```

**Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_generate.py -v
```

Expected: FAIL with ImportError

**Step 4: Implement generate.py**

```python
"""Main generation orchestration."""

from __future__ import annotations

from pathlib import Path

from llmstxt_gen.config import Config
from llmstxt_gen.convert import html_to_markdown


def md_path_to_html_path(site_dir: Path, md_path: str) -> Path:
    """Convert docs/foo.md path to site/foo/index.html path."""
    if md_path == "index.md":
        return site_dir / "index.html"
    return site_dir / md_path.replace(".md", "") / "index.html"


def md_path_to_md_url(site_url: str, md_path: str) -> str:
    """Convert docs/foo.md path to direct markdown URL."""
    if md_path == "index.md":
        return f"{site_url}/index.md"
    return f"{site_url}/{md_path.replace('.md', '')}/index.md"


def generate_llms_txt(
    config: Config,
    site_dir: Path,
    verbose: bool = False,
) -> tuple[str, str]:
    """Generate llms.txt and llms-full.txt content.

    Args:
        config: Resolved configuration.
        site_dir: Path to built HTML site directory.
        verbose: Whether to print progress.

    Returns:
        Tuple of (llms_txt content, llms_full_txt content).
    """
    # Build llms.txt (index)
    llms_lines = [f"# {config.site_name}", ""]

    if config.site_description:
        llms_lines.append(f"> {config.site_description}")
        llms_lines.append("")

    if config.markdown_description:
        llms_lines.append(config.markdown_description.strip())
        llms_lines.append("")

    # Build llms-full.txt header
    full_lines = [f"# {config.site_name}", ""]

    if config.site_description:
        full_lines.append(f"> {config.site_description}")
        full_lines.append("")

    # Process sections
    all_pages: list[tuple[str, str]] = []

    for section_name, pages in config.sections.items():
        llms_lines.append(f"## {section_name}")
        llms_lines.append("")

        for page in sorted(pages):
            title = config.get_page_title(page)
            md_url = md_path_to_md_url(config.site_url, page)
            llms_lines.append(f"- [{title}]({md_url})")
            all_pages.append((title, page))

        llms_lines.append("")

    # Convert pages for llms-full.txt
    for title, md_path in all_pages:
        html_path = md_path_to_html_path(site_dir, md_path)

        if not html_path.exists():
            if verbose:
                print(f"Warning: {html_path} not found, skipping")
            continue

        html = html_path.read_text(encoding="utf-8")
        content = html_to_markdown(html, config.content_selector)

        if content:
            full_lines.append(f"## {title}")
            full_lines.append("")
            full_lines.append(content)
            full_lines.append("")

    llms_txt = "\n".join(llms_lines)
    llms_full_txt = "\n".join(full_lines)

    return llms_txt, llms_full_txt
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_generate.py -v
```

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/llmstxt_gen/generate.py tests/test_generate.py tests/fixtures/site/
git commit -m "feat: add generation orchestration"
```

---

## Task 5: CLI Integration (cli.py)

**Files:**
- Modify: `src/llmstxt_gen/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing tests**

Create `tests/test_cli.py`:
```python
"""Tests for CLI."""

from pathlib import Path

from typer.testing import CliRunner

from llmstxt_gen.cli import app

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "llms.txt" in result.stdout.lower() or "Generate" in result.stdout


def test_cli_missing_config():
    result = runner.invoke(app, ["--config", "/nonexistent/mkdocs.yml"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()


def test_cli_missing_site_dir():
    result = runner.invoke(app, [
        "--config", str(FIXTURES / "mkdocs_with_llmstxt.yml"),
        "--site-dir", "/nonexistent/site",
    ])
    assert result.exit_code == 1


def test_cli_success(tmp_path: Path):
    # Copy fixtures to tmp_path for output
    import shutil
    shutil.copytree(FIXTURES / "site", tmp_path / "site")

    result = runner.invoke(app, [
        "--config", str(FIXTURES / "mkdocs_with_llmstxt.yml"),
        "--site-dir", str(tmp_path / "site"),
        "--output-dir", str(tmp_path / "site"),
    ])

    assert result.exit_code == 0
    assert (tmp_path / "site" / "llms.txt").exists()
    assert (tmp_path / "site" / "llms-full.txt").exists()
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: Some tests fail

**Step 3: Implement full cli.py**

```python
"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from llmstxt_gen import __version__
from llmstxt_gen.config import load_config
from llmstxt_gen.generate import generate_llms_txt

app = typer.Typer(
    help="Generate llms.txt from built HTML documentation.",
    no_args_is_help=False,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"llmstxt-gen {__version__}")
        raise typer.Exit()


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Option("--config", "-c", help="Path to mkdocs.yml config file"),
    ] = Path("mkdocs.yml"),
    site_dir: Annotated[
        Path,
        typer.Option("--site-dir", "-s", help="Path to built HTML site directory"),
    ] = Path("site"),
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output-dir", "-o", help="Output directory (defaults to site-dir)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed progress"),
    ] = False,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=version_callback, is_eager=True, help="Show version"),
    ] = False,
) -> None:
    """Generate llms.txt and llms-full.txt from built HTML documentation."""
    # Resolve output directory
    out_dir = output_dir or site_dir

    # Validate inputs
    if not config.exists():
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(1)

    if not site_dir.exists():
        typer.echo(f"Error: Site directory not found: {site_dir}", err=True)
        raise typer.Exit(1)

    # Load config
    try:
        cfg = load_config(config)
    except Exception as e:
        typer.echo(f"Error loading config: {e}", err=True)
        raise typer.Exit(1)

    if verbose:
        typer.echo(f"Site: {cfg.site_name}")
        typer.echo(f"Sections: {list(cfg.sections.keys())}")

    # Generate content
    llms_txt, llms_full_txt = generate_llms_txt(
        config=cfg,
        site_dir=site_dir,
        verbose=verbose,
    )

    # Write output files
    out_dir.mkdir(parents=True, exist_ok=True)

    llms_path = out_dir / "llms.txt"
    llms_path.write_text(llms_txt, encoding="utf-8")

    full_path = out_dir / cfg.full_output
    full_path.write_text(llms_full_txt, encoding="utf-8")

    typer.echo(f"Generated {llms_path} ({len(llms_txt):,} bytes)")
    typer.echo(f"Generated {full_path} ({len(llms_full_txt):,} bytes)")


if __name__ == "__main__":
    app()
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: All tests PASS

**Step 5: Run all tests**

```bash
uv run pytest -v
```

Expected: All tests PASS

**Step 6: Test manually**

```bash
cd ~/code/prek/feat-llms-txt
uvx --from ~/code/llmstxt-gen llmstxt-gen --help
uvx --from ~/code/llmstxt-gen llmstxt-gen --config mkdocs.yml --site-dir site
```

**Step 7: Commit**

```bash
cd ~/code/llmstxt-gen
git add src/llmstxt_gen/cli.py tests/test_cli.py
git commit -m "feat: add Typer CLI"
```

---

## Task 6: Final Polish

**Files:**
- Update: `README.md` (if needed)
- Create: `LICENSE`

**Step 1: Create LICENSE file**

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 2: Run linting**

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

**Step 3: Final test run**

```bash
uv run pytest -v --tb=short
```

**Step 4: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

**Step 5: Tag release**

```bash
git tag v0.1.0
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Project setup | - |
| 2 | HTML→Markdown conversion | 4 tests |
| 3 | Config loading | 4 tests |
| 4 | Generation orchestration | 3 tests |
| 5 | CLI integration | 4 tests |
| 6 | Final polish | - |

Total: ~15 tests, 6 tasks
