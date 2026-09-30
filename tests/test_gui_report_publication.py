from unittest.mock import Mock

import pytest

import MethodenAnalyser3 as app


def prepare_file(monkeypatch, tmp_path):
    source = tmp_path / "source.py"
    source.write_text("print('Grüße')\n", encoding="utf-8")
    monkeypatch.setattr(app.filedialog, "askopenfilename", lambda **_kw: str(source))
    monkeypatch.setattr(app, "messagebox", Mock())
    return source


def test_formatting_failure_does_not_create_partial_file_report(tmp_path, monkeypatch):
    prepare_file(monkeypatch, tmp_path)
    monkeypatch.setattr(app, "generate_report", Mock(side_effect=["display", RuntimeError("format failure")]))
    app.run_analysis(Mock(), Mock())
    assert not (tmp_path / "source_analysis.txt").exists()
    app.messagebox.showwarning.assert_called_once()


def test_project_replace_error_preserves_previous_report(tmp_path, monkeypatch):
    report = tmp_path / "project_analysis.txt"
    report.write_bytes(b"previous report")
    monkeypatch.setattr(app.filedialog, "askdirectory", lambda **_kw: str(tmp_path))
    monkeypatch.setattr(app, "messagebox", Mock())

    def fail(*_args):
        raise OSError("replace failure")

    monkeypatch.setattr(app.os, "replace", fail)
    app.run_project_analysis(Mock(), Mock())
    assert report.read_bytes() == b"previous report"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["project_analysis.txt"]
    app.messagebox.showerror.assert_called_once()


def test_concurrent_file_report_is_preserved_and_export_gets_new_name(tmp_path, monkeypatch):
    prepare_file(monkeypatch, tmp_path)
    monkeypatch.setattr(app, "generate_report", lambda _result: "EXPORT Grüße")
    first = tmp_path / "source_analysis.txt"
    actual_link = app.os.link
    actual_choose = app.create_safe_filename
    attempts = []

    def choose(*args):
        chosen = actual_choose(*args)
        if not first.exists():
            first.write_bytes(b"concurrent report")
        return chosen

    def publish(staged, destination):
        attempts.append(destination)
        return actual_link(staged, destination)

    monkeypatch.setattr(app, "create_safe_filename", choose)
    monkeypatch.setattr(app.os, "link", publish)
    app.run_analysis(Mock(), Mock())
    assert first.read_bytes() == b"concurrent report"
    assert "EXPORT Grüße" in (tmp_path / "source_1_analysis.txt").read_text(encoding="utf-8")
    assert len(attempts) == 2
    assert sorted(p.name for p in tmp_path.iterdir()) == ["source.py", "source_1_analysis.txt", "source_analysis.txt"]
    app.messagebox.showwarning.assert_not_called()


@pytest.mark.parametrize("failure", ["fsync", "link"])
def test_file_report_publication_failure_leaves_no_partial_output(tmp_path, monkeypatch, failure):
    source = prepare_file(monkeypatch, tmp_path)
    original = source.read_bytes()

    def fail(*_args):
        raise OSError("publication failure")

    monkeypatch.setattr(app.os, failure, fail)
    app.run_analysis(Mock(), Mock())
    assert source.read_bytes() == original
    assert sorted(p.name for p in tmp_path.iterdir()) == ["source.py"]
    app.messagebox.showwarning.assert_called_once()


def test_project_report_success_replaces_previous_content(tmp_path, monkeypatch):
    report = tmp_path / "project_analysis.txt"
    report.write_bytes(b"previous report")
    monkeypatch.setattr(app.filedialog, "askdirectory", lambda **_kw: str(tmp_path))
    monkeypatch.setattr(app, "messagebox", Mock())
    monkeypatch.setattr(app, "generate_project_report", lambda *_args, **_kwargs: "REPORT Grüße")
    app.run_project_analysis(Mock(), Mock())
    assert report.read_text(encoding="utf-8") == "REPORT Grüße"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["project_analysis.txt"]
    app.messagebox.showerror.assert_not_called()
