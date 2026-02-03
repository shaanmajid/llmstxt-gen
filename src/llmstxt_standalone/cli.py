"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from ruamel.yaml import YAML

from llmstxt_standalone import __version__
from llmstxt_standalone.config import load_config
from llmstxt_standalone.generate import build_llms_output, write_markdown_files


def version_callback(value: bool) -> None:
    """Print version and exit if --version flag is set."""
    if value:
        typer.echo(f"llmstxt-standalone {__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="Generate llms.txt from built HTML documentation.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
) -> None:
    """Generate llms.txt from built HTML documentation."""


@app.command()
def build(
    config: Annotated[
        Path,
        typer.Option("--config", "-c", help="Path to mkdocs.yml config file"),
    ] = Path("mkdocs.yml"),
    site_dir: Annotated[
        Path,
        typer.Option("--site-dir", "-s", help="Path to built HTML site directory"),
    ] = Path("site"),
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir", "-o", help="Output directory (defaults to site-dir)"
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Preview what would be generated without writing files",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress output (exit code only)"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed progress"),
    ] = False,
) -> None:
    """Generate llms.txt and llms-full.txt from built MkDocs site."""
    # Resolve output directory
    out_dir = output_dir or site_dir

    # quiet overrides verbose
    if quiet:
        verbose = False

    def log(msg: str, color: str = "green", err: bool = False) -> None:
        if not quiet:
            typer.secho(msg, fg=color, err=err)

    def _safe_output_path(name: str) -> Path:
        path = Path(name)
        if path.is_absolute() or path.drive:
            raise ValueError("full_output must be a relative path")
        if ".." in path.parts:
            raise ValueError("full_output must not contain '..'")
        return path

    # Validate inputs
    if not config.exists():
        log(f"Error: Config file not found: {config}", color="red", err=True)
        raise typer.Exit(1)

    if not site_dir.exists():
        log(f"Error: Site directory not found: {site_dir}", color="red", err=True)
        log(
            "Hint: Run 'mkdocs build' first to generate the HTML documentation.",
            color="yellow",
            err=True,
        )
        raise typer.Exit(1)

    # Load config
    try:
        cfg = load_config(config)
    except Exception as e:
        log(f"Error loading config: {e}", color="red", err=True)
        raise typer.Exit(1) from None

    # Validate sections
    if not cfg.sections:
        log("Error: No sections configured.", color="red", err=True)
        log(
            "Add a 'nav' to your mkdocs.yml, or configure 'sections' "
            "in the llmstxt plugin.",
            color="yellow",
            err=True,
        )
        raise typer.Exit(1)

    if verbose:
        typer.echo(f"Site: {cfg.site_name}")
        typer.echo(f"Sections: {list(cfg.sections.keys())}")
        if dry_run:
            typer.echo("Dry run - no files will be written")

    # Generate content
    llms_build = build_llms_output(
        config=cfg,
        site_dir=site_dir,
    )
    try:
        markdown_files = write_markdown_files(
            llms_build.pages,
            output_dir=out_dir,
            use_directory_urls=cfg.use_directory_urls,
            dry_run=dry_run,
        )
    except (OSError, ValueError) as exc:
        log(f"Error writing markdown files: {exc}", color="red", err=True)
        raise typer.Exit(1) from None

    # Define output paths
    llms_path = out_dir / "llms.txt"
    try:
        full_output_path = _safe_output_path(cfg.full_output)
    except ValueError as exc:
        log(f"Error: Invalid full_output: {exc}", color="red", err=True)
        raise typer.Exit(1) from None
    full_path = out_dir / full_output_path

    # Write output files (skip in dry-run mode)
    if dry_run:
        action = "Would generate"
        color = "yellow"
    else:
        action = "Generated"
        color = "green"
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            llms_path.write_text(llms_build.llms_txt, encoding="utf-8")
            full_path.write_text(llms_build.llms_full_txt, encoding="utf-8")
        except OSError as exc:
            log(f"Error writing output files: {exc}", color="red", err=True)
            raise typer.Exit(1) from None

    log(f"{action} {llms_path} ({len(llms_build.llms_txt):,} bytes)", color)
    log(f"{action} {full_path} ({len(llms_build.llms_full_txt):,} bytes)", color)
    log(f"{action} {len(markdown_files)} markdown files", color)

    if verbose and llms_build.skipped:
        log("Skipped files:", color="yellow", err=True)
        for path, reason in llms_build.skipped:
            log(f"- {path} ({reason})", color="yellow", err=True)

    if llms_build.warnings:
        log("Warnings:", color="yellow", err=True)
        for warning in llms_build.warnings:
            log(f"- {warning}", color="yellow", err=True)


@app.command()
def init(
    config: Annotated[
        Path,
        typer.Option("--config", "-c", help="Path to mkdocs.yml config file"),
    ] = Path("mkdocs.yml"),
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing llmstxt section"),
    ] = False,
) -> None:
    """Add llmstxt plugin config to mkdocs.yml."""
    if not config.exists():
        typer.secho(
            f"Error: Config file not found: {config}",
            fg="red",
            err=True,
        )
        typer.secho(
            "Create one first or specify path with --config.",
            fg="yellow",
            err=True,
        )
        raise typer.Exit(1)

    yaml = YAML()
    yaml.preserve_quotes = True

    with open(config, encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        data = {}

    # Check for existing llmstxt plugin
    plugins = data.get("plugins", [])
    if plugins is None:
        plugins = []
    if not isinstance(plugins, (list, dict)):
        typer.secho(
            "Error: 'plugins' must be a list or mapping in mkdocs.yml.",
            fg="red",
            err=True,
        )
        raise typer.Exit(1)
    data["plugins"] = plugins
    has_llmstxt = False

    if isinstance(plugins, list):
        for plugin in plugins:
            if plugin == "llmstxt" or (
                isinstance(plugin, dict) and "llmstxt" in plugin
            ):
                has_llmstxt = True
                break
    elif isinstance(plugins, dict):
        has_llmstxt = "llmstxt" in plugins

    if has_llmstxt and not force:
        typer.secho(
            "Error: llmstxt plugin already configured.",
            fg="red",
            err=True,
        )
        typer.secho(
            "Use --force to overwrite existing configuration.",
            fg="yellow",
            err=True,
        )
        raise typer.Exit(1)

    # Remove existing llmstxt if force is set
    if has_llmstxt and force:
        if isinstance(plugins, list):
            plugins = [
                p
                for p in plugins
                if p != "llmstxt" and not (isinstance(p, dict) and "llmstxt" in p)
            ]
            data["plugins"] = plugins
        elif isinstance(plugins, dict):
            del plugins["llmstxt"]

    # Create the llmstxt plugin entry with commented example
    llmstxt_entry = {
        "llmstxt": {
            # We'll add comments after writing
        }
    }

    if isinstance(data["plugins"], list):
        data["plugins"].append(llmstxt_entry)
    else:
        # Preserve dict-style plugins
        data["plugins"]["llmstxt"] = {}

    # Write the file
    with open(config, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    # Now add comments using string manipulation since ruamel.yaml comment API is complex
    content = config.read_text(encoding="utf-8")
    ends_with_newline = content.endswith("\n")

    # Find the llmstxt entry and add commented example below it
    commented_example_lines = [
        "# markdown_description: |",
        "#   Additional context for LLMs.",
        "# sections:",
        "#   Getting Started:",
        "#     - index.md",
    ]

    def _comment_indent(line: str) -> int:
        leading = len(line) - len(line.lstrip(" "))
        if line.lstrip().startswith("- "):
            return leading + 4
        return leading + 2

    def _format_commented_example(indent: int) -> list[str]:
        prefix = " " * indent
        return [f"{prefix}{line}" for line in commented_example_lines]

    # Look for the llmstxt entry and add commented example below it
    lines = content.splitlines()
    new_lines: list[str] = []
    inserted = False
    for line in lines:
        stripped = line.strip()
        if not inserted and stripped == "llmstxt: {}":
            indent = _comment_indent(line)
            new_lines.append(line.replace("llmstxt: {}", "llmstxt:"))
            new_lines.extend(_format_commented_example(indent))
            inserted = True
            continue
        if not inserted and stripped == "llmstxt:":
            indent = _comment_indent(line)
            new_lines.append(line)
            new_lines.extend(_format_commented_example(indent))
            inserted = True
            continue
        new_lines.append(line)
    content = "\n".join(new_lines)
    if ends_with_newline:
        content += "\n"

    config.write_text(content, encoding="utf-8")

    typer.echo(f"Added llmstxt plugin to {config}")


@app.command()
def validate(
    config: Annotated[
        Path,
        typer.Option("--config", "-c", help="Path to mkdocs.yml config file"),
    ] = Path("mkdocs.yml"),
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Exit code only, no output"),
    ] = False,
) -> None:
    """Check config file validity."""
    try:
        cfg = load_config(config)

        # Compute total pages
        total_pages = sum(len(pages) for pages in cfg.sections.values())

        if not quiet:
            typer.echo(f"Config valid: {config}")
            typer.echo(f"  Site: {cfg.site_name}")
            typer.echo(f"  Sections: {len(cfg.sections)}")
            typer.echo(f"  Pages: {total_pages}")

    except FileNotFoundError:
        if not quiet:
            typer.secho(f"Config invalid: {config}", fg="red", err=True)
            typer.secho(f"  Error: File not found: {config}", fg="red", err=True)
        raise typer.Exit(1) from None

    except ValueError as e:
        if not quiet:
            typer.secho(f"Config invalid: {config}", fg="red", err=True)
            typer.secho(f"  Error: {e}", fg="red", err=True)
        raise typer.Exit(1) from None

    except Exception as e:
        if not quiet:
            typer.secho(f"Config invalid: {config}", fg="red", err=True)
            typer.secho(f"  Error: {e}", fg="red", err=True)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
