import pytest
from click.testing import CliRunner

from lzkit.cli import cli
from lzkit.file import FormatType, dump, dumps, load, loads


def test_file_convert_csv_to_json(tmp_path):
    runner = CliRunner()
    csv_file = tmp_path / "input.csv"
    csv_file.write_text("name,age\ntest,99\n", encoding="utf-8")

    out_file = tmp_path / "output.json"
    result = runner.invoke(
        cli, ["file", "convert", str(csv_file), str(out_file)]
    )
    assert result.exit_code == 0, result.output
    assert "Converted" in result.output

    # Confirm the input was removed
    assert not csv_file.exists()

    # Confirm out_file is JSON
    data = out_file.read_text()
    assert data.startswith("[")
    assert data.endswith("]\n") or data.endswith("]")


def test_file_format_stdin_jsonl(tmp_path):
    runner = CliRunner()
    out_file = tmp_path / "formatted.json"

    # Provide JSONL content via stdin
    content = '{"a":1}\n{"a":2}\n'
    result = runner.invoke(
        cli, ["file", "format", "-", str(out_file)], input=content
    )
    assert result.exit_code == 0, result.output

    # out_file should be JSON because extension is .json
    # So let's see if it parsed line by line and wrote a JSON array or dict?
    text = out_file.read_text()

    # It's .csv -> let's see. Actually, we didn't do forced extension.
    # Actually we do: path_out is formatted.json => .json => so we do JSON
    # This is a detail: the code is using dump with extension => .json => so we get a JSON array or dict
    assert text.startswith("[")  # implies we got a JSON array
    assert text.endswith("]\n") or text.endswith("]")


def test_format_type():
    assert FormatType.from_path("my_file.json") == FormatType.JSON
    assert FormatType.from_path("my_file.csv").delimiter == ","
    assert FormatType.from_path("what.unknown") == FormatType.UNKNOWN
    assert FormatType.from_path("what.jsonl").delimiter is None


def test_dumps_json_format_unknown():
    # Single object
    fmt, data = loads('{"name": "test", "value": 123}', FormatType.UNKNOWN)
    assert fmt == FormatType.JSON
    out_str = dumps(data, fmt)

    # re-parse
    fmt2, data2 = loads(out_str, FormatType.UNKNOWN)
    assert data2 == data


def test_json_load_dump(tmp_path):
    data_dict = {"foo": 123, "bar": "baz"}
    testfile = tmp_path / "example.json"

    # Dump a dict
    success = dump(testfile, data_dict, indent=2)
    assert success is True
    assert testfile.exists()

    # Load it back
    loaded = load(testfile)
    assert loaded == data_dict


def test_csv_load_dump(tmp_path):
    rows = [
        {"name": "Alice", "age": "30"},
        {"name": "Bob", "age": "25"},
    ]
    testfile = tmp_path / "people.csv"

    # Dump a list of dicts
    success = dump(testfile, rows)
    assert success is True
    assert testfile.exists()

    # Load it back
    loaded = load(testfile)
    assert loaded == rows


def test_loads_json_variants():
    content = '{"name": "test"}'
    fmt, data = loads(content, FormatType.UNKNOWN)
    assert fmt == FormatType.JSON
    assert data == {"name": "test"}

    content2 = '[{"name": "test1"}, {"name": "test2"}]'
    fmt2, data2 = loads(content2, FormatType.UNKNOWN)
    assert fmt2 == FormatType.JSON
    assert data2 == [{"name": "test1"}, {"name": "test2"}]

    # JSONL
    content3 = '{"name": "test1"}\n{"name": "test2"}'
    fmt3, data3 = loads(content3, FormatType.UNKNOWN)
    assert fmt3 == FormatType.JSONL
    assert data3 == [{"name": "test1"}, {"name": "test2"}]


def test_unsupported_extension(tmp_path):
    data = {"some": "thing"}
    weird_file = tmp_path / "unknown.xyz"

    # Dump -> should return False, because unsupported extension
    ok = dump(weird_file, data)
    assert ok is False

    # Load -> should return None
    loaded = load(weird_file)
    assert loaded is None


def test_file_not_found():
    loaded = load("/not/exist/file.json")
    assert loaded is None


def test_file_not_found_raise():
    with pytest.raises(FileNotFoundError):
        load("/not/exist/file.json", raise_on_error=True)


def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.touch()  # create empty file
    loaded = load(empty_file)
    assert loaded is None


def test_empty_file_raise(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.touch()
    with pytest.raises(ValueError):
        load(empty_file, raise_on_error=True)


def test_jsonl_load_dump(tmp_path):
    data_list = [
        {"id": 1, "text": "first"},
        {"id": 2, "text": "second"},
    ]
    testfile = tmp_path / "items.jsonl"

    # Dump
    ok = dump(testfile, data_list)
    assert ok is True

    # Load
    loaded = load(testfile)
    assert loaded == data_list


def test_fieldnames_csv(tmp_path):
    # If user explicitly wants certain field order
    rows = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    file_csv = tmp_path / "ordered.csv"

    dump(file_csv, rows, fieldnames=["age", "name"])
    text = file_csv.read_text()
    # Check that age is written first
    lines = text.strip().split("\n")
    assert lines[0] == "age,name"
    # load -> won't necessarily preserve field order in the result dict,
    # but we confirm the header is correct


def test_tomlkit_keep_comments():
    example_toml_with_comments = """
# This is a comment
[files]
indent = 2
""".strip()

    fmt, content = loads(example_toml_with_comments, FormatType.UNKNOWN)
    assert fmt == FormatType.TOML
    assert content.keys() == {"files"}
    assert dumps(content, FormatType.TOML) == example_toml_with_comments
