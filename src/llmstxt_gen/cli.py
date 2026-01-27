"""Command-line interface."""

import typer

app = typer.Typer(help="Generate llms.txt from built HTML documentation.")


@app.command()
def main() -> None:
    """Generate llms.txt and llms-full.txt."""
    typer.echo("Not implemented yet")
    raise typer.Exit(1)
