from click.testing import CliRunner

from lzkit.cli import cli


def test_hello():
    runner = CliRunner()

    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert "Verbosity: 0\nHello, World!" in result.output

    result = runner.invoke(cli, ["hello", "Joe"])
    assert result.exit_code == 0
    assert "Verbosity: 0\nHello, Joe!" in result.output

    result = runner.invoke(cli, ["hello", "-vv", "Joe"])
    assert result.exit_code == 0
    assert "Verbosity: 2\nHello, Joe!" in result.output
