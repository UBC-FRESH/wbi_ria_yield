"""Module entry point for `python -m femic`."""

from __future__ import annotations

from femic.cli.main import app


def main() -> None:
    """Invoke the Typer application for `python -m femic`."""
    app()


if __name__ == "__main__":
    main()
