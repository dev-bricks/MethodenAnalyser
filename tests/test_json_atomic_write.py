import json
import stat

import pytest

import MethodenAnalyser3 as app


def test_serialization_error_preserves_previous_report(tmp_path):
    target = tmp_path / "report.json"
    target.write_bytes(b'{"previous": true}\n')
    with pytest.raises(TypeError):
        app.write_json_report({"first": "valid", "later": object()}, str(target))
    assert target.read_bytes() == b'{"previous": true}\n'
    assert sorted(p.name for p in tmp_path.iterdir()) == ["report.json"]


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("failure", ["fsync", "replace"])
def test_write_failure_preserves_target_and_removes_temp(tmp_path, monkeypatch, existing, failure):
    target = tmp_path / "report.json"
    if existing:
        target.write_bytes(b"previous report")

    def fail(*_args):
        raise OSError("injected write failure")

    monkeypatch.setattr(app.os, failure, fail)
    with pytest.raises(OSError, match="injected"):
        app.write_json_report({"new": "Grüße"}, str(target))
    assert target.exists() == existing
    if existing:
        assert target.read_bytes() == b"previous report"
    assert sorted(p.name for p in tmp_path.iterdir()) == (["report.json"] if existing else [])


def test_success_publishes_complete_utf8_report(tmp_path, monkeypatch):
    target = tmp_path / "nested" / "report.json"
    actual_replace = app.os.replace
    observed = []

    def replace(staged, destination):
        staged_path = app.pathlib.Path(staged)
        assert staged_path.parent == target.parent
        assert json.loads(staged_path.read_text(encoding="utf-8")) == {"text": "Grüße"}
        assert not target.exists()
        observed.append(True)
        actual_replace(staged, destination)

    monkeypatch.setattr(app.os, "replace", replace)
    assert app.write_json_report({"text": "Grüße"}, str(target)) == str(target)
    assert observed == [True]
    assert target.read_bytes().endswith(b"\n")
    assert json.loads(target.read_text(encoding="utf-8")) == {"text": "Grüße"}
    assert sorted(p.name for p in target.parent.iterdir()) == ["report.json"]


@pytest.mark.parametrize("existing", [False, True])
def test_short_write_never_publishes_partial_json(tmp_path, monkeypatch, existing):
    target = tmp_path / "report.json"
    if existing:
        target.write_bytes(b"previous report")
    actual_temp = app.tempfile.NamedTemporaryFile

    class ShortWriter:
        def __init__(self, *args, **kwargs):
            self.handle = actual_temp(*args, **kwargs)

        def __enter__(self):
            self.handle.__enter__()
            return self

        def __exit__(self, *args):
            return self.handle.__exit__(*args)

        @property
        def name(self):
            return self.handle.name

        def write(self, data):
            return self.handle.write(data[:4])

    monkeypatch.setattr(app.tempfile, "NamedTemporaryFile", ShortWriter)
    with pytest.raises(OSError, match="Incomplete JSON"):
        app.write_json_report({"text": "Grüße"}, str(target))
    assert target.exists() == existing
    if existing:
        assert target.read_bytes() == b"previous report"
    assert sorted(p.name for p in tmp_path.iterdir()) == (["report.json"] if existing else [])


def test_replace_preserves_existing_file_mode(tmp_path):
    target = tmp_path / "report.json"
    target.write_bytes(b"old")
    target.chmod(0o640)
    mode = stat.S_IMODE(target.stat().st_mode)
    app.write_json_report({"new": True}, str(target))
    assert stat.S_IMODE(target.stat().st_mode) == mode
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}


def test_report_symlink_is_preserved(tmp_path):
    destination = tmp_path / "destination.json"
    destination.write_bytes(b"old")
    link = tmp_path / "report.json"
    try:
        link.symlink_to(destination)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    assert app.write_json_report({"new": True}, str(link)) == str(link)
    assert link.is_symlink()
    assert json.loads(destination.read_text(encoding="utf-8")) == {"new": True}


def test_read_only_report_is_preserved(tmp_path):
    target = tmp_path / "report.json"
    target.write_bytes(b"previous report")
    target.chmod(stat.S_IRUSR)
    try:
        with pytest.raises(PermissionError):
            app.write_json_report({"new": True}, str(target))
        assert target.read_bytes() == b"previous report"
        assert sorted(p.name for p in tmp_path.iterdir()) == ["report.json"]
    finally:
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)
