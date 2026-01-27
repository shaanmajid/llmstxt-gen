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
