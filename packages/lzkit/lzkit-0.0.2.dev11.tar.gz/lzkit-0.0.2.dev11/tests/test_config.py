from click.testing import CliRunner

from lzkit.cli import cli


def test_config_new_show(tmp_path, monkeypatch):
    # Force LZKIT_PATH to a tmp dir
    monkeypatch.setenv("LZKIT_PATH", str(tmp_path))

    runner = CliRunner()
    # config new
    result_new = runner.invoke(cli, ["config", "new"])
    assert result_new.exit_code == 0, result_new.output
    # Check the file was created
    conf_file = tmp_path / "config.toml"
    assert conf_file.exists()

    # config show
    result_show = runner.invoke(cli, ["config", "show"])
    assert result_show.exit_code == 0, result_show.output
    assert "Current config as pydantic model:" in result_show.output
