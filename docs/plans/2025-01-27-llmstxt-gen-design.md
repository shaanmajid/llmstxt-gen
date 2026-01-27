# llmstxt-gen Design

## Overview

**llmstxt-gen** is a CLI tool that generates `/llms.txt` and `/llms-full.txt` from built HTML documentation, following the [llms.txt spec](https://llmstxt.org/).

### Target Users

- Zensical users (can't use MkDocs plugins)
- Anyone with built HTML docs who wants llms.txt without MkDocs plugin infrastructure

### Core Approach

1. Read config from `mkdocs.yml` (llmstxt plugin format or nav fallback)
2. Parse built HTML with BeautifulSoup
3. Convert to Markdown with markdownify + mdformat
4. Write `llms.txt` (index) and `llms-full.txt` (full content)

### Non-Goals (v1)

- Supporting non-MkDocs config formats (Hugo, Sphinx, etc.)
- Running as a MkDocs plugin (that's what mkdocs-llmstxt is for)
- Watch mode / live reload

## CLI Interface

```bash
# Basic usage (auto-detect from cwd)
llmstxt-gen

# Explicit paths
llmstxt-gen --config mkdocs.yml
llmstxt-gen --site-dir ./build
llmstxt-gen --output-dir ./build

# Help
llmstxt-gen --help
llmstxt-gen --version
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--config` | `mkdocs.yml` | Path to config file |
| `--site-dir` | `site/` | Built HTML directory |
| `--output-dir` | same as site-dir | Where to write output files |
| `--verbose` / `-v` | false | Show detailed progress |

### Exit Codes

- 0: Success
- 1: Error (missing config, missing site dir, etc.)

## Config Resolution

### Priority Order

1. CLI flags (highest)
2. `llmstxt` plugin config in mkdocs.yml
3. `nav` from mkdocs.yml (fallback)
4. Defaults (lowest)

### Config Options

From mkdocs.yml llmstxt plugin:

```yaml
plugins:
  - llmstxt:
      markdown_description: |
        Extra context for LLMs...
      full_output: llms-full.txt      # default
      content_selector: .my-content   # optional, has sensible default
      sections:
        Getting Started:
          - index.md
          - install.md
```

### Nav Fallback

If no `llmstxt` plugin config exists, sections are derived from the `nav` structure automatically.

## Package Structure

```
llmstxt-gen/
├── src/
│   └── llmstxt_gen/
│       ├── __init__.py      # version, public API
│       ├── __main__.py      # python -m llmstxt_gen
│       ├── cli.py           # typer CLI
│       ├── config.py        # config loading & resolution
│       ├── convert.py       # HTML → Markdown conversion
│       └── generate.py      # orchestration (main logic)
├── tests/
│   ├── test_config.py
│   ├── test_convert.py
│   └── fixtures/            # sample HTML, mkdocs.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

### Module Responsibilities

- **cli.py** - Typer app, argument parsing, calls `generate()`
- **config.py** - Load mkdocs.yml, extract llmstxt config, nav fallback
- **convert.py** - BeautifulSoup + markdownify logic (autoclean, html_to_markdown)
- **generate.py** - Main orchestration: load config → convert pages → write output

## Dependencies

### Runtime

```toml
dependencies = [
    "typer>=0.9.0",
    "pyyaml>=6.0",
    "beautifulsoup4>=4.12",
    "markdownify>=0.11",
    "mdformat>=0.7",
    "mdformat-tables>=1.0",
]
```

### Dev

```toml
[dependency-groups]
dev = ["pytest", "ruff", "ty", "prek"]
```

## Content Extraction

### Default Selector Chain

```python
content = (
    soup.select_one(custom_selector) if custom_selector
    else soup.select_one(".md-content__inner")  # Material for MkDocs
    or soup.select_one("article")
    or soup.select_one("main")
    or soup
)
```

### Autoclean Rules

Remove from HTML before conversion:
- Images and SVGs
- Permalink anchors (`.headerlink`)
- Twemoji elements
- Tab labels (`.tabbed-labels`)
- Code block line number tables

## Output Format

### llms.txt

```markdown
# Site Name

> Site description

Custom markdown description from config...

## Section Name

- [Page Title](https://site.com/page/index.md)
- [Another Page](https://site.com/another/index.md)
```

### llms-full.txt

```markdown
# Site Name

> Site description

## Page Title

Full converted markdown content...

## Another Page

More content...
```

## Future Considerations

- sitemap.xml support (auto-discover pages without config)
- Other config formats (Hugo, Sphinx)
- Custom autoclean rules via config
