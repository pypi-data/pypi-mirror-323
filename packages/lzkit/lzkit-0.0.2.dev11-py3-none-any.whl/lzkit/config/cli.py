import click

from . import load_config, new_config


@click.group()
def config_cli():
    """Create and configure Kits."""
    pass


@config_cli.command("new")
@click.option("--overwrite", is_flag=True, default=False)
def new_cmd(overwrite):
    """
    Creates a new default config in LZKIT_PATH if none exists.
    """
    new_config(overwrite=overwrite)
    click.echo("Initialized new config (if it didn't already exist).")


@config_cli.command("show")
def show_cmd():
    """
    Display the loaded config and its final Pydantic model (including defaults).
    """
    cfg = load_config()
    click.echo("Current config as pydantic model:")
    click.echo(repr(cfg))

    # If you want to show the raw dict (with defaults included):
    click.echo("As dictionary:")
    click.echo(str(cfg.model_dump()))
