import click

from .config.cli import config_cli
from .file.cli import file_cli


class State:
    def __init__(self):
        self.verbosity = 0


pass_state = click.make_pass_decorator(State, ensure=True)


def verbosity_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.verbosity = value
        return value

    return click.option(
        "-v",
        "--verbose",
        count=True,
        expose_value=False,
        help="Enables verbosity.",
        callback=callback,
    )(f)


def common_options(f):
    f = verbosity_option(f)
    return f


def _cli():
    pass


cli = click.group(_cli)


@cli.command()
@common_options
@click.argument("name", type=str, default="World")
@pass_state
def hello(state, name):
    click.echo(f"Verbosity: {state.verbosity}")
    click.echo(f"Hello, {name}!")


# noinspection PyTypeChecker
cli.add_command(config_cli, "config")

# noinspection PyTypeChecker
cli.add_command(file_cli, "file")
