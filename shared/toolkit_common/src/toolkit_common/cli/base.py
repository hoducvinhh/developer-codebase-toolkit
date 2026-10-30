"""Click base decorators and standardized options."""

from typing import Any, Callable

import click


def common_options(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to attach standard CLI options to any Click command."""
    f = click.option(
        "--format",
        "-f",
        "output_format",
        type=click.Choice(["terminal", "json", "markdown", "sarif"], case_sensitive=False),
        default="terminal",
        help="Output display or export format.",
        show_default=True,
    )(f)
    f = click.option(
        "--output",
        "-o",
        type=click.Path(dir_okay=False, writable=True),
        default=None,
        help="Optional path to write the output report file.",
    )(f)
    f = click.option(
        "--config",
        "-c",
        type=click.Path(exists=True, dir_okay=False),
        default=None,
        help="Path to custom configuration file.",
    )(f)
    f = click.option(
        "--quiet",
        "-q",
        is_flag=True,
        default=False,
        help="Suppress informational stdout output (only show errors/results).",
    )(f)
    f = click.option(
        "--verbose",
        "-v",
        is_flag=True,
        default=False,
        help="Enable detailed debug/trace logging.",
    )(f)
    f = click.option(
        "--no-color",
        is_flag=True,
        default=False,
        help="Disable ANSI color and style formatting.",
    )(f)
    return f
