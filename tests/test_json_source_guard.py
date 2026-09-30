import os

import pytest

import MethodenAnalyser3 as app


@pytest.mark.parametrize("mode", ["file", "project"])
@pytest.mark.parametrize("alias", ["direct", "hardlink", "symlink"])
def test_cli_json_cannot_replace_analyzed_source(tmp_path, mode, alias):
    source = tmp_path / "source.py"
    original = b"import os\n"
    source.write_bytes(original)
    output = source
    if alias != "direct":
        output = tmp_path / "alias.json"
        try:
            if alias == "hardlink":
                os.link(source, output)
            else:
                output.symlink_to(source)
        except OSError as exc:
            pytest.skip(f"{alias} unavailable: {exc}")
    runner = app._run_cli_file if mode == "file" else app._run_cli_project
    assert runner(str(source if mode == "file" else tmp_path), str(output)) == app.EXIT_ANALYSIS_ERROR
    assert source.read_bytes() == original
    assert output.read_bytes() == original


def test_project_json_cannot_replace_source_with_syntax_error(tmp_path):
    source = tmp_path / "broken.py"
    original = b"def invalid(:\n"
    source.write_bytes(original)
    assert app._run_cli_project(str(tmp_path), str(source)) == app.EXIT_ANALYSIS_ERROR
    assert source.read_bytes() == original
