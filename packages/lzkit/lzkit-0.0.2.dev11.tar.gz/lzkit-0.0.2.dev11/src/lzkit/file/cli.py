from pathlib import Path

import click

from . import dump, load


@click.group()
def file_cli():
    """File transformation functions."""
    pass


@file_cli.command("convert")
@click.argument("path_in", type=click.Path())
@click.argument("path_out", type=click.Path())
@click.option("--keep", is_flag=True, help="Keep source file on success.")
def convert_cmd(path_in, path_out, keep):
    """
    Convert data from src -> dest using extension-based format detection.
    If path_in='-', read from stdin (auto-detect or force?).
    """
    data = load(path_in)

    ok = dump(path_out, data)

    if not ok:
        click.echo(f"Failed to dump to {path_out}", err=True)
        raise SystemExit(1)

    click.echo(f"Converted {path_in} -> {path_out}")
    if not keep and path_in != "-":
        Path(path_in).unlink(missing_ok=True)
        click.echo(f"Removed {path_in}")


@file_cli.command("format")
@click.argument("path_in", type=click.Path())
@click.argument("path_out", type=click.Path(), required=False)
@click.option(
    "--fmt",
    type=click.Choice(["json", "csv", "psv", "tsv", "jsonl"]),
    help="Force output format if you don't want to rely on path_out extension.",
)
def format_cmd(path_in, path_out, fmt):
    """
    Re-format or pretty-print an existing file. If path_out not provided, overwrites path_in.
    If --fmt is given, that sets the output extension or logic.
    """
    data = load(path_in)

    # If no path_out, overwrite input
    if not path_out:
        path_out = path_in

    # If user provided --fmt, we can rename path_out with that extension
    if fmt and path_out != "-":
        new_ext = f".{fmt}"
        path_out_obj = Path(path_out)
        path_out = str(path_out_obj.with_suffix(new_ext))

    # Dump with config / defaults
    ok = dump(path_out, data)

    if not ok:
        click.echo(f"Failed to write {path_out}", err=True)
        raise SystemExit(1)

    click.echo(f"Reformatted {path_in} -> {path_out}")
